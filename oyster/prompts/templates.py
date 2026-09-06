"""Prompt wording, copied from the build spec. It is load-bearing: it determines every
number in the results table, so it is specified, not improvised, and never edited at runtime."""

OUTPUT_CONTRACT = """
Respond with JSON only, no prose, no markdown fence:
{"findings": [{"file": str, "line_start": int, "line_end": int,
               "category": "logic"|"security"|"style",
               "description": str, "confidence": float}]}
Use line numbers from the diff's new-file side. If you find nothing, return
{"findings": []}. Never invent a file path that does not appear in the diff.
"""

CHEAP_SCANNER = (
    """You are a fast first-pass code reviewer. Scan the diff and flag anything
that looks suspicious. Favor recall over precision: it is better to flag a hunk that turns out
fine than to miss a real defect. Do not explain at length, one sentence per finding.

Categories: logic (wrong behavior, off-by-one, null handling, race), security (injection,
authz, secrets, unsafe deserialization), style (naming, dead code, formatting).

DIFF:
{diff}
"""
    + OUTPUT_CONTRACT
)

DEEP_REVIEWER = (
    """You are a thorough code reviewer. Analyze the diff for real defects.
Favor precision over recall: report a finding only when you can state what breaks and under
what condition.

Categories: logic, security, style, as defined by the impact on behavior rather than surface
appearance.

DIFF:
{diff}
{upstream_block}
"""
    + OUTPUT_CONTRACT
)

UPSTREAM_BLOCK = """
An earlier pass flagged these locations. Treat them as hints, not conclusions. Confirm, refute
or extend them, and report defects they missed.

EARLIER FINDINGS:
{upstream_findings}
"""

CRITIC = (
    """You are reviewing another reviewer's output, not the code directly. For each
finding below, decide whether it is a real defect or a false positive. Then state what the
reviewer likely missed.

Return findings you believe are real, plus any additional defects you identify. Drop findings
you judge to be false positives.

DIFF:
{diff}

FINDINGS UNDER REVIEW:
{upstream_findings}
"""
    + OUTPUT_CONTRACT
)

TEMPLATES: dict[str, str] = {
    "cheap_scanner": CHEAP_SCANNER,
    "deep_reviewer": DEEP_REVIEWER,
    "critic": CRITIC,
}
