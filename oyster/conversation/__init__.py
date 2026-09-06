"""Conversation mode: run the corpus through any chat subscription with prompt packs.

No API, no CLI, no key. The engine is driven by a fixture-filling loop:

1. `pack` runs every calibration node and every catalog path over the corpus with a provider
   that answers from recorded fixtures and records each request it cannot answer. Those
   pending requests become a pack: numbered prompt blocks to paste into a chat, plus a
   manifest that ties every block to its fixture key.
2. You paste each message into a chat on the model the block names, and save the reply.
3. `ingest` parses the replies and stores them as fixtures keyed exactly as the mock provider
   looks them up. Token counts are estimated from characters because a chat UI reports none.
4. Repeat. The next `pack` finds round 1 answered and emits round 2 (the cascade's second
   node and the critic, whose prompts depend on round 1 findings), then round 3. When `pack`
   reports nothing pending, `eval --provider mock --fixtures <dir>` renders the table.

The executor, prompt templates and matcher are untouched, so the prompts are byte-identical to
what the API providers send: a block is `render(prompt_key, diff, upstream)` with the diff in
its slot. What differs, and is labeled in the results: token counts are estimates (chars // 4)
rather than API-reported, latency is not measured, and in a batched pack several requests
share one chat context, which is a transport wrapper around the unchanged per-request text.
"""

import json
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from oyster.cost import estimate_tokens
from oyster.evaluation import calibrate, evaluate
from oyster.executor import parse_findings
from oyster.graph.catalog import CATALOG
from oyster.providers.mock_provider import EMPTY_RESPONSE, MISS_LATENCY_S, MockProvider, fixture_key
from oyster.types import Completion, CorpusCase, ModelBinding
from oyster.types import Path as GraphPath

__all__ = [
    "PackProvider",
    "PendingRequest",
    "collect_pending",
    "ingest",
    "write_pack",
]

DIFF_SLOT = "DIFF:\n\n"

BATCH_WRAPPER = (
    "You will receive {count} independent code review requests below, each in its own section "
    "headed by a request id. Handle each one exactly as its own instructions say, using only "
    "that request's diff. Reply with a single JSON object and nothing else:\n"
    '{{"responses": {{"<request id>": <that request\'s JSON reply>, ...}}}}\n'
    "with one entry per request id."
)


@dataclass(frozen=True)
class PendingRequest:
    id: str
    key: str
    model_id: str
    system: str
    user: str
    cached_prefix: str

    @property
    def prompt(self) -> str:
        """The single chat message: the rendered template with the diff back in its slot."""
        if self.cached_prefix and DIFF_SLOT in self.user:
            body = self.user.replace(DIFF_SLOT, f"DIFF:\n{self.cached_prefix}\n", 1)
        else:
            body = "\n\n".join(part for part in (self.cached_prefix, self.user) if part)
        return f"{self.system}\n\n{body}" if self.system else body


class PackProvider(MockProvider):
    """Answers from fixtures; records every miss instead of only logging it."""

    def __init__(self, fixtures_dir: Path):
        super().__init__(fixtures_dir)
        self.pending: dict[str, PendingRequest] = {}

    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion:
        key = fixture_key(model_id, system, user, cached_prefix)
        if (self.fixtures_dir / f"{key}.json").is_file():
            return super().complete(model_id, system, user, cached_prefix)
        if key not in self.pending:
            self.pending[key] = PendingRequest(
                id=f"r{len(self.pending) + 1}",
                key=key,
                model_id=model_id,
                system=system,
                user=user,
                cached_prefix=cached_prefix or "",
            )
        prefix = cached_prefix or ""
        return Completion(
            text=EMPTY_RESPONSE,
            input_tokens=estimate_tokens(prefix + system + user),
            cached_input_tokens=estimate_tokens(prefix),
            output_tokens=estimate_tokens(EMPTY_RESPONSE),
            latency_s=MISS_LATENCY_S,
            model_id=model_id,
        )


def collect_pending(
    cases: Sequence[CorpusCase],
    fixtures_dir: Path,
    bindings: dict[str, ModelBinding],
    paths: Sequence[GraphPath] = CATALOG,
) -> list[PendingRequest]:
    """Every request the calibration pass and the catalog paths need that no fixture answers
    yet, in first-needed order. Later rounds only appear once earlier rounds are answered,
    because their prompts are built from the earlier findings."""
    provider = PackProvider(fixtures_dir)
    calibrate(cases, provider, bindings, paths)
    evaluate(paths, cases, provider, bindings)
    return list(provider.pending.values())


def write_pack(
    pending: Sequence[PendingRequest], out_dir: Path, *, batch_size: int = 20
) -> tuple[Path, Path]:
    """pack.md (messages to paste) and manifest.json (ids, keys, estimated input tokens)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = [
        {**asdict(request), "estimated_input_tokens": estimate_tokens(request.prompt)}
        for request in pending
    ]
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    by_model: dict[str, list[PendingRequest]] = {}
    for request in pending:
        by_model.setdefault(request.model_id, []).append(request)

    lines = [
        "# OYSTER prompt pack",
        "",
        (
            f"{len(pending)} request(s). Paste each message into a fresh chat on the model it "
            "names, copy the reply verbatim into a responses file, then run `ingest`."
        ),
        "",
    ]
    message_number = 0
    for model_id, requests in by_model.items():
        for start in range(0, len(requests), max(1, batch_size)):
            batch = requests[start : start + max(1, batch_size)]
            message_number += 1
            ids = ", ".join(request.id for request in batch)
            lines += [
                f"## Message {message_number}: model `{model_id}`, requests {ids}",
                "",
                "Copy everything between the BEGIN and END markers as one message.",
                "",
                "----- BEGIN MESSAGE -----",
            ]
            if len(batch) > 1:
                lines += [BATCH_WRAPPER.format(count=len(batch)), ""]
                for request in batch:
                    lines += [f"### {request.id}", "", request.prompt.rstrip(), ""]
            else:
                lines += [batch[0].prompt.rstrip(), ""]
            lines += ["----- END MESSAGE -----", ""]
            if len(batch) > 1:
                lines += [
                    (
                        'Reply format: one JSON object `{"responses": {"r..": {...}}}`. '
                        "Save it under a `### responses` header, or bare, in the responses file."
                    ),
                    "",
                ]
            else:
                lines += [
                    (
                        f"Reply format: the JSON object alone. Save it under a "
                        f"`### {batch[0].id}` header in the responses file."
                    ),
                    "",
                ]
    pack_path = out_dir / "pack.md"
    pack_path.write_text("\n".join(lines), encoding="utf-8")
    return pack_path, out_dir / "manifest.json"


_HEADER = re.compile(r"^###\s+(r\d+|responses)\s*$", re.MULTILINE)
_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _json_objects(text: str) -> list[dict]:
    """Every top-level JSON object in a chunk of text, fenced or bare."""
    found: list[dict] = []
    for match in _FENCE.finditer(text):
        try:
            found.append(json.loads(match.group(1)))
        except json.JSONDecodeError:
            continue
    if found:
        return found
    decoder = json.JSONDecoder()
    index = 0
    while index < len(text):
        start = text.find("{", index)
        if start < 0:
            break
        try:
            value, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            index = start + 1
            continue
        if isinstance(value, dict):
            found.append(value)
        index = end
    return found


def _replies(responses_text: str) -> tuple[dict[str, object], set[str]]:
    """(request id -> reply object, request ids that have a `### rN` header). Replies come
    from `### rN` sections, `{"responses": {...}}` objects, or a single bare reply when the
    file holds exactly one request's answer."""
    replies: dict[str, object] = {}
    headed: set[str] = set()
    sections = _HEADER.split(responses_text)
    # sections = [preamble, id1, body1, id2, body2, ...]
    chunks = [("", sections[0])] + [
        (sections[i], sections[i + 1]) for i in range(1, len(sections) - 1, 2)
    ]
    for header, body in chunks:
        if header and header != "responses":
            headed.add(header)
        for obj in _json_objects(body):
            if isinstance(obj.get("responses"), dict):
                for request_id, reply in obj["responses"].items():
                    replies[str(request_id)] = reply
            elif header and header != "responses":
                replies[header] = obj
            elif "findings" in obj:
                replies.setdefault("__single__", obj)
    return replies, headed


@dataclass(frozen=True)
class IngestReport:
    written: tuple[str, ...]
    missing: tuple[str, ...]
    unparseable: tuple[str, ...]


def ingest(
    manifest_path: Path,
    responses_text: str,
    fixtures_dir: Path,
    *,
    model_label: str,
    latency_s: float = 0.0,
) -> IngestReport:
    """Store chat replies as fixtures. Token counts are chars // 4 estimates and are labeled
    as such by the model_label the caller passes (for example "chat:claude-sonnet-5")."""
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    replies, headed = _replies(responses_text)
    if "__single__" in replies and len(manifest) == 1:
        replies[manifest[0]["id"]] = replies.pop("__single__")
    fixtures_dir = Path(fixtures_dir)
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    missing: list[str] = []
    unparseable: list[str] = []
    for entry in manifest:
        reply = replies.get(entry["id"])
        if reply is None:
            # A header with nothing parseable under it is a bad reply, not an absent one.
            (unparseable if entry["id"] in headed else missing).append(entry["id"])
            continue
        text = json.dumps(reply) if not isinstance(reply, str) else reply
        if parse_findings(text) is None:
            unparseable.append(entry["id"])
            continue
        request = PendingRequest(
            entry["id"],
            entry["key"],
            entry["model_id"],
            entry["system"],
            entry["user"],
            entry["cached_prefix"],
        )
        fixture = {
            "text": text,
            "input_tokens": estimate_tokens(request.prompt),
            "cached_input_tokens": 0,
            "output_tokens": estimate_tokens(text),
            "latency_s": latency_s,
            "model_id": model_label,
        }
        (fixtures_dir / f"{entry['key']}.json").write_text(
            json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        written.append(entry["id"])
    return IngestReport(tuple(written), tuple(missing), tuple(unparseable))
