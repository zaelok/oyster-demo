"""Prompt rendering. Wording lives in templates.py and is never modified at runtime.

Rendering fills the three slots {diff}, {upstream_block} and {upstream_findings} in a single
regex pass, so text inside the diff or the findings is never re-substituted, and the literal
braces of the JSON output contract survive untouched (str.format would choke on them).
"""

import json
import re
from collections.abc import Sequence
from dataclasses import asdict

from oyster.prompts.templates import TEMPLATES, UPSTREAM_BLOCK
from oyster.types import Finding

__all__ = ["TEMPLATES", "UPSTREAM_BLOCK", "render", "render_findings", "render_messages"]

_SLOT = re.compile(r"\{(diff|upstream_block|upstream_findings)\}")


def render_findings(findings: Sequence[Finding]) -> str:
    """One JSON object per line, in the order given."""
    return "\n".join(json.dumps(asdict(finding), sort_keys=True) for finding in findings)


def _fill(template: str, values: dict[str, str]) -> str:
    return _SLOT.sub(lambda match: values.get(match.group(1), match.group(0)), template)


def render(prompt_key: str, diff: str, upstream_findings: Sequence[Finding] = ()) -> str:
    """The full logical prompt: {diff} substituted, the upstream block present only when there
    are upstream findings. This is the auditable form of what a node was asked."""
    rendered_findings = render_findings(upstream_findings)
    upstream_block = ""
    if upstream_findings:
        upstream_block = _fill(UPSTREAM_BLOCK, {"upstream_findings": rendered_findings})
    return _fill(
        TEMPLATES[prompt_key],
        {"diff": diff, "upstream_block": upstream_block, "upstream_findings": rendered_findings},
    )


def render_messages(
    prompt_key: str, diff: str, upstream_findings: Sequence[Finding] = ()
) -> tuple[str, str, str]:
    """Provider form of render(): (system, user, cached_prefix).

    The diff travels only as cached_prefix. The provider places it in a cache-controlled block
    ahead of everything else, so every node on the same case shares one cache hit (the diff is
    the cache-hit prefix, architecture §1.2). The user body is the rendered template with the
    {diff} slot left empty: wording stays byte-identical to the template and the diff appears
    exactly once in the request, never duplicated into the user message (spec §4).
    """
    return "", render(prompt_key, "", upstream_findings), diff
