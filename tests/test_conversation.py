import json

from oyster.conversation import PendingRequest, collect_pending, ingest, write_pack
from oyster.evaluation import evaluate
from oyster.graph.catalog import CATALOG
from oyster.prompts import render, render_messages
from oyster.providers import MockProvider
from tests.conftest import finding_json


def _reply_for_all(manifest_path, finding_text):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    responses = {entry["id"]: json.loads(finding_text) for entry in manifest}
    return json.dumps({"responses": responses})


def test_prompt_puts_the_diff_back_in_its_slot(corpus_case):
    system, user, cached = render_messages("deep_reviewer", corpus_case.diff)
    request = PendingRequest("r1", "k", "m", system, user, cached)
    assert request.prompt == render("deep_reviewer", corpus_case.diff)


def test_rounds_converge_and_the_table_shows_catches(corpus_case, bindings, tmp_path):
    fixtures = tmp_path / "fixtures"
    cases = [corpus_case]

    round1 = collect_pending(cases, fixtures, bindings)
    assert len(round1) == 3, "cheap scanner, deep reviewer and critic, each once for one case"
    assert {r.model_id for r in round1} == {"mock-cheap", "mock-strong"}
    pack_path, manifest_path = write_pack(round1, tmp_path / "round-1", batch_size=20)
    pack_text = pack_path.read_text(encoding="utf-8")
    assert "----- BEGIN MESSAGE -----" in pack_text
    assert "### r1" in pack_text and "### r3" in pack_text
    assert corpus_case.diff.strip() in pack_text

    report = ingest(
        manifest_path,
        _reply_for_all(manifest_path, finding_json("pricing.py", 7, 7)),
        fixtures,
        model_label="chat:test",
    )
    assert report.written == ("r1", "r2", "r3") and not report.missing

    round2 = collect_pending(cases, fixtures, bindings)
    assert len(round2) == 2, "path B node 2 and path C node 2 now have their upstream"
    assert all("EARLIER FINDINGS" in r.user or "FINDINGS UNDER REVIEW" in r.user for r in round2)
    assert any('"line_start": 7' in r.user for r in round2)
    _, manifest2 = write_pack(round2, tmp_path / "round-2")
    ingest(
        manifest2,
        _reply_for_all(manifest2, finding_json("auth.py", 23, 24, "security")),
        fixtures,
        model_label="chat:test",
    )

    round3 = collect_pending(cases, fixtures, bindings)
    assert len(round3) == 1, "path C node 3"
    _, manifest3 = write_pack(round3, tmp_path / "round-3")
    ingest(
        manifest3,
        _reply_for_all(manifest3, finding_json("auth.py", 23, 24, "security")),
        fixtures,
        model_label="chat:test",
    )

    assert collect_pending(cases, fixtures, bindings) == []

    results, reports = evaluate(CATALOG, cases, MockProvider(fixtures), bindings)
    by_path = {report.path_id: report for report in reports}
    assert by_path["A"].caught_strict == ("case-01-b1",)
    assert by_path["B"].caught_strict == ("case-01-b2",)
    assert by_path["C"].caught_strict == ("case-01-b2",)
    assert all(result.node_results[0].completion.model_id == "chat:test" for result in results)
    assert all(result.cost.dollars > 0 for result in results)


def test_single_request_pack_and_bare_reply(corpus_case, bindings, tmp_path):
    fixtures = tmp_path / "fixtures"
    pending = collect_pending([corpus_case], fixtures, bindings)[:1]
    pack_path, manifest_path = write_pack(pending, tmp_path / "single", batch_size=1)
    text = pack_path.read_text(encoding="utf-8")
    assert "independent code review requests" not in text
    report = ingest(manifest_path, finding_json("pricing.py", 7, 7), fixtures, model_label="c")
    assert report.written == ("r1",)


def test_ingest_reports_missing_and_unparseable(corpus_case, bindings, tmp_path):
    fixtures = tmp_path / "fixtures"
    pending = collect_pending([corpus_case], fixtures, bindings)
    _, manifest_path = write_pack(pending, tmp_path / "round-1")
    responses = "### r1\n```json\n" + finding_json("pricing.py", 7, 7) + "\n```\n### r2\nnot json\n"
    report = ingest(manifest_path, responses, fixtures, model_label="c")
    assert report.written == ("r1",)
    assert report.missing == ("r3",)
    assert report.unparseable == ("r2",)
