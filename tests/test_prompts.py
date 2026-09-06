from oyster.prompts import TEMPLATES, render, render_findings, render_messages
from oyster.prompts.templates import OUTPUT_CONTRACT
from oyster.types import Finding

DIFF = "--- a/x.py\n+++ b/x.py\n@@ -1,2 +1,2 @@\n-a\n+b\n c\n"
UPSTREAM = (
    Finding("x.py", 3, 5, "logic", "off by one", 0.7),
    Finding("y.py", 10, 12, "security", "injection", 0.9),
)


def test_deep_reviewer_without_upstream_has_no_earlier_findings():
    prompt = render("deep_reviewer", DIFF)
    assert "EARLIER FINDINGS" not in prompt
    assert DIFF in prompt
    assert "{upstream_block}" not in prompt


def test_deep_reviewer_with_upstream_lists_each_file_and_range():
    prompt = render("deep_reviewer", DIFF, UPSTREAM)
    assert "EARLIER FINDINGS" in prompt
    for finding in UPSTREAM:
        assert f'"file": "{finding.file}"' in prompt
        assert f'"line_start": {finding.line_start}' in prompt
        assert f'"line_end": {finding.line_end}' in prompt


def test_critic_renders_findings_under_review():
    prompt = render("critic", DIFF, UPSTREAM)
    assert "FINDINGS UNDER REVIEW" in prompt
    assert "{upstream_findings}" not in prompt
    assert '"file": "y.py"' in prompt


def test_output_contract_braces_survive_rendering():
    for key in TEMPLATES:
        prompt = render(key, DIFF, UPSTREAM)
        assert OUTPUT_CONTRACT.strip() in prompt
        assert '{"findings": []}' in prompt


def test_render_findings_is_one_json_object_per_line():
    lines = render_findings(UPSTREAM).splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("{") and lines[0].endswith("}")


def test_render_messages_puts_diff_only_in_cached_prefix():
    system, user, cached = render_messages("cheap_scanner", DIFF)
    assert cached == DIFF
    assert DIFF not in user
    assert DIFF not in system
    assert "You are a fast first-pass code reviewer" in user
    assert "{diff}" not in user


def test_text_inside_diff_is_not_resubstituted():
    tricky = "--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n+print('{upstream_findings}')\n"
    prompt = render("critic", tricky, UPSTREAM)
    assert "print('{upstream_findings}')" in prompt
