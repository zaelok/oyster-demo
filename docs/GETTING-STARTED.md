# Getting started, and validating against an API vendor

This is the practical companion to the README. It covers the offline run you get from a bare
clone, the three ways to produce new numbers, how to add an API vendor, and how to compare
runs without fooling yourself.

## 1. A bare clone reproduces the committed table with no key

```bash
uv sync
uv run pytest -q                                  # 130 offline tests
uv run python -m oyster.cli eval --provider mock --fixtures fixtures/conversation/haiku45-sonnet5 --label "replay"
```

The last command replays the recorded replies under `fixtures/conversation/` and regenerates
the table in `results/conversation-haiku45-sonnet5/results.md` to the cent. That is the
reproducibility claim: every number in a committed table comes from a committed fixture, and
the fixture is keyed by a hash of the exact prompt that produced it.

No `uv`? Any Python 3.12+ works:

```bash
python -m venv .venv && .venv/Scripts/python -m pip install pydantic pydantic-settings anthropic rich pytest ruff
.venv/Scripts/python -m pytest -q
```

## 2. Three ways to make new numbers

| route | what pays | token counts | latency | prompt fidelity |
|---|---|---|---|---|
| `--provider anthropic` | API key, real dollars | API-reported, split into input / cache read / output | measured | exact: diff in a cache-controlled system block, template in the user turn |
| `--provider claude-code` | Claude subscription quota | API-reported via the CLI's JSON result | CLI `duration_api_ms` | exact prompt; CLI adds a small wrapper of its own |
| conversation mode (`pack` / `ingest`) | any chat subscription | estimated, `chars // 4` | not measured | exact per-request text; batched messages share one chat context |

All three go through the same executor, templates and matcher. Only the provider changes,
and the results header names which one ran. The selector and the table do not know or care.

### API route

```bash
cp .env.example .env        # set OYSTER_ANTHROPIC_API_KEY (or export ANTHROPIC_API_KEY)
uv run python -m tools.run_matrix --provider anthropic
```

`run_matrix` runs calibrate, eval and select for each model pair in its `CONFIGS` table,
writes `results/<config>/{priors,results}.json`, `results.md`, `run.log`, and a combined
`results/summary.md`. Each run prints a rough cost estimate and, without `--yes`, waits for
confirmation. Every completion is recorded as a mock fixture under `fixtures/mock/` so the
run replays offline afterwards. Rates are placeholders in `oyster/config.py` and the matrix;
verify them against the vendor's price list before a paid run and keep the values in the
results header honest.

### Subscription routes

See the README section "Running on a subscription instead of an API key". The CLI route needs
a one-time `claude setup-token` with the token in `.env` as
`OYSTER_CLAUDE_CODE_OAUTH_TOKEN` (or exported as `CLAUDE_CODE_OAUTH_TOKEN`, or a stored
`claude auth login`); the conversation route needs nothing but a chat window.

## 3. Adding another API vendor

The provider contract is five lines in `oyster/types.py`:

```python
class ModelProvider(Protocol):
    def complete(
        self, model_id: str, system: str, user: str, cached_prefix: str | None = None
    ) -> Completion: ...
```

Implement it in `oyster/providers/<vendor>_provider.py`, return a `Completion`, and register
the name in the CLI's `--provider` choices. Rules that keep the numbers comparable:

1. **Where the pieces go.** `cached_prefix` is the diff. Put it first, in whatever slot the
   vendor caches (a system message, a cached-content object, a prefix block). `system` is
   usually empty. `user` is the rendered template with the diff slot left empty; send it as the
   user turn. Never paste the diff into the user turn as well.
2. **Token counts come from the response, never from an estimate.** Map the vendor's usage
   object onto `Completion`: `input_tokens` is the total prompt tokens including any cached
   share, `cached_input_tokens` is the cached share, `output_tokens` is everything the model
   generated including reasoning tokens if the vendor bills them as output. Record 0 for a
   field the vendor omits; do not fill it in.
3. **Latency** is `time.perf_counter()` around the successful call.
4. **Retry** only 429 and 5xx, a few attempts with backoff; raise anything else.
5. **Rates** come from environment variables or `.env` (`OYSTER_*_RATE_IN/OUT`), so the
   pricing formula in `oyster/cost` stays vendor-neutral. `cache_discount` is the fraction of
   the input rate waived on cached tokens; set it to what the vendor actually charges.
6. **Tests use a stub client**, never the network: assert the cached count is read from usage,
   that 429 retries and 400 does not, and that the diff lands in the cached slot.
7. Add the module to the allowlist in `tests/test_integration.py`; it may import only
   `oyster.types` (and `oyster.cost` if it needs the estimator for a mock path).

Usage field names, as documented by the vendors at the time of writing; check them against the
current SDK before relying on them:

| vendor | total prompt tokens | cached share | output tokens | notes |
|---|---|---|---|---|
| Anthropic Messages | `usage.input_tokens + cache_read_input_tokens + cache_creation_input_tokens` | `cache_read_input_tokens` | `usage.output_tokens` | thinking tokens are inside `output_tokens`; cache writes cost more than the discount models |
| OpenAI Chat Completions / Responses | `usage.prompt_tokens` (`input_tokens` on Responses) | `usage.prompt_tokens_details.cached_tokens` | `usage.completion_tokens` (`output_tokens`) | reasoning tokens are inside output on reasoning models |
| Google Gemini | `usageMetadata.promptTokenCount` | `usageMetadata.cachedContentTokenCount` | `candidatesTokenCount + thoughtsTokenCount` | explicit context caching is a separate object with its own TTL |

Any OpenAI-compatible endpoint (self-hosted, gateway, third-party) fits the OpenAI row.

## 3a. Long runs: resume and workers

Every API or CLI run records each completion as a fixture (`--record`, default
`fixtures/mock`; `tools/run_matrix.py` uses `fixtures/<provider>`). A request whose fixture
already exists is replayed, not re-sent, so an interrupted run resumes by re-issuing the same
command, and prompts shared between calibrate and eval are paid for once. The run's summary
line says how many calls were made and how many replayed.

`--workers N` runs the cases of each path on N threads. Provider calls are I/O bound (an HTTP
request or a CLI process), so four workers cut wall time by roughly four; results and their
order do not depend on it. Start with 4 on a subscription and lower it if the CLI reports
usage limits; the provider retries transient limits three times with backoff before failing,
and a failed run resumes from its fixtures.

## 3b. Two corpus tiers

`oyster/corpus/cases/` is the reviewed tier: 17 cases a person signed off on, the ground
truth behind every committed number. `oyster/corpus/cases-auto/` is the auto tier: cases
built by `tools/build_corpus.py` from merged fix PRs in public repositories and accepted by
mechanical gates only; nobody checked the labels (its README says exactly what is real and
what is a guess). `--corpus` is repeatable, so a run can take either tier or both:

```bash
uv run python -m oyster.cli eval --provider claude-code --corpus oyster/corpus/cases-auto --out results-auto.md
uv run python -m oyster.cli eval --provider claude-code --corpus oyster/corpus/cases --corpus oyster/corpus/cases-auto
```

Report the tiers separately. A catch rate over unreviewed labels measures the labels as much
as the model; the honest sentence is "on the auto tier, N cases, unreviewed", never a merged
number. Rebuild the tier with `uv run python -m tools.build_corpus`; a warm `.corpus-cache/`
makes the rebuild offline and identical, a cold one re-searches GitHub and picks up newer PRs.

## 4. Comparing runs without fooling yourself

- **Same corpus commit.** The results header records it. Two tables from different corpus
  commits are two experiments.
- **Prompts are byte-identical across providers by construction**, so a difference between
  runs is the model, its settings, or the transport, never the wording.
- **Compare per case, not just totals.** `results.json` retains every `PathResult` and
  `MatchReport`; a paired look (which bugs did A catch that C missed) is what explained the
  first run's surprise. Totals hide it.
- **21 bugs is a small sample.** A one- or two-bug difference between paths is noise. Say so.
  Strict and loose are separate columns; false positives are their own column; report all
  three, never the flattering one.
- **Label what differed.** `--label` puts the provider, model settings and token-count method
  in the header. A table without that line is not comparable to anything.
- **Record and commit fixtures** so the run replays; without them a number cannot be traced.

### What to expect when moving from chat to an API run

Same weights, different wrapper. The differences that could move numbers:

- the chat app adds its own system prompt and formatting rules; the API run sends only the diff
  and the template;
- thinking settings differ (chat "medium" versus the API default), and thinking tokens are
  invisible in chat but billed as output on the API;
- batched chat messages put up to twenty requests in one context; the API sends one per call;
- the API gets cache hits on the diff prefix across a case's nodes; chat gets none;
- both sample at temperature 1, so two API runs will not agree exactly either.

Prediction, written down before the API run so it can be checked: catch rates within about
two bugs of the conversation-mode table for the same model pair; dollars for the strong-model
paths (B, C) noticeably higher on the API because thinking tokens are counted; path A cheaper
per call once the diff is a cache hit; latency real instead of blank. The ordering of the
three paths should not change. If it does, that is the interesting result.

## 5. If something is off

- `pack` says nothing is pending but the table is empty: the fixtures directory passed to
  `eval` is not the one `ingest` wrote to, or `.env` names different model ids than when the
  pack was made. Keys are hashes of model id plus prompt.
- `ingest` reports "not a JSON findings object": the reply was prose or a truncated object.
  Re-ask the chat for JSON only and replace that section.
- `No Python at ...` from `.venv\Scripts\python.exe`: the venv's base interpreter moved.
  Delete `.venv` and run `uv sync` (or `uv venv --python <path>`) again.
- `Neither OYSTER_ANTHROPIC_API_KEY nor ANTHROPIC_API_KEY is set`: intentional; the API
  route never runs by accident.
