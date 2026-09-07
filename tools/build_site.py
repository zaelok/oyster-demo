"""Build a single-file results page from the committed runs.

Reads every results/<run>/ directory (results.json, priors.json, results.md header), the
corpus and the catalog, and writes site/index.html with the data inlined, so the page works
from a local file, from GitHub Pages, or anywhere else with no server and no dependencies.

    python -m tools.build_site            # writes site/index.html
    python -m tools.build_site --out docs/site/index.html
"""

import argparse
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from oyster.corpus import load_corpora
from oyster.evaluation import LIMITATIONS
from oyster.graph.catalog import CATALOG

_MODEL_LINE = re.compile(r"^\s*(?:Models:\s*)?([\w-]+)=(\S+) @ \$([\d.]+)/\$([\d.]+) per 1M")


def _header(results_md: Path) -> dict:
    info: dict = {"models": {}}
    if not results_md.exists():
        return info
    for line in results_md.read_text(encoding="utf-8").splitlines()[:12]:
        if line.startswith("Generated:"):
            info["generated"] = line.split(":", 1)[1].strip()
        elif line.startswith("Corpus:"):
            info["corpus_line"] = line.split(":", 1)[1].strip()
            match = re.search(r"corpus commit (\S+)", line)
            info["corpus_commit"] = match.group(1) if match else "unknown"
        elif line.startswith("Provider:"):
            info["provider"] = line.split(":", 1)[1].strip()
        else:
            match = _MODEL_LINE.match(line)
            if match:
                info["models"][match.group(1)] = {
                    "model_id": match.group(2),
                    "rate_in": float(match.group(3)),
                    "rate_out": float(match.group(4)),
                }
    return info


def run_dirs(results_root: Path) -> list[Path]:
    """Every directory holding a results.json, one or two levels below results/: the first
    runs sit at results/<run>/, run_matrix writes results/<batch>/<config>/."""
    found = []
    for first in sorted(p for p in results_root.iterdir() if p.is_dir()):
        if (first / "results.json").exists():
            found.append(first)
        found.extend(
            second
            for second in sorted(p for p in first.iterdir() if p.is_dir())
            if (second / "results.json").exists()
        )
    return found


def collect(results_root: Path, corpus_dirs: Sequence[Path]) -> dict:
    runs = []
    for run_dir in run_dirs(results_root):
        results_json = run_dir / "results.json"
        priors = {}
        if (run_dir / "priors.json").exists():
            priors = json.loads((run_dir / "priors.json").read_text(encoding="utf-8"))
        data = json.loads(results_json.read_text(encoding="utf-8"))
        runs.append(
            {
                "name": run_dir.relative_to(results_root).as_posix(),
                **_header(run_dir / "results.md"),
                "priors": priors,
                "results": data["results"],
                "reports": data["reports"],
            }
        )
    cases = [asdict(case) for case in load_corpora([Path(d) for d in corpus_dirs])]
    paths = [asdict(path) for path in CATALOG]
    return {
        "built": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "paths": paths,
        "cases": cases,
        "runs": runs,
        "limitations": LIMITATIONS,
    }


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OYSTER results</title>
<style>
:root { color-scheme: light dark; --bg:#fbfaf7; --fg:#1d1d1b; --muted:#6b6a66; --line:#dcd9d2; --card:#ffffff; --acc:#0b6e4f; --warn:#b3541e; --bad:#a83232; --bar:#cfe8dd; }
@media (prefers-color-scheme: dark) { :root { --bg:#161615; --fg:#ecebe6; --muted:#a09e97; --line:#3a3936; --card:#1f1f1d; --acc:#5fc39a; --warn:#e6905c; --bad:#e07070; --bar:#244b3b; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width:1100px; margin:0 auto; padding:32px 20px 80px; }
h1 { font-size:28px; margin:0 0 4px; letter-spacing:-0.01em; }
h2 { font-size:19px; margin:36px 0 10px; }
.sub { color:var(--muted); margin:0 0 18px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px 18px; margin:12px 0; }
table { border-collapse:collapse; width:100%; font-variant-numeric:tabular-nums; }
th, td { text-align:left; padding:7px 10px; border-bottom:1px solid var(--line); vertical-align:top; }
th { font-weight:600; color:var(--muted); font-size:13px; }
td.num, th.num { text-align:right; }
.bar { position:relative; }
.bar span.fill { position:absolute; left:0; top:4px; bottom:4px; background:var(--bar); border-radius:3px; z-index:0; }
.bar span.txt { position:relative; z-index:1; }
.pill { display:inline-block; padding:1px 8px; border-radius:999px; font-size:12px; border:1px solid var(--line); color:var(--muted); }
.pill.ok { color:var(--acc); border-color:var(--acc); }
.pill.bad { color:var(--bad); border-color:var(--bad); }
.pill.warn { color:var(--warn); border-color:var(--warn); }
.controls { display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; }
.controls label { display:block; font-size:13px; color:var(--muted); }
.controls input[type=range] { width:100%; }
.controls output { font-weight:600; color:var(--fg); }
.grid { overflow-x:auto; }
.matrix td.hit { color:var(--acc); font-weight:600; }
.matrix td.miss { color:var(--bad); }
.matrix tr { cursor:pointer; }
.matrix tr:hover td { background:color-mix(in srgb, var(--acc) 8%, transparent); }
pre { background:color-mix(in srgb, var(--fg) 5%, var(--card)); border:1px solid var(--line); border-radius:8px; padding:12px; overflow-x:auto; font:12.5px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
pre .add { color:var(--acc); } pre .del { color:var(--bad); } pre .hunk { color:var(--muted); }
.small { font-size:13px; color:var(--muted); }
select { font:inherit; padding:4px 8px; border-radius:6px; border:1px solid var(--line); background:var(--card); color:var(--fg); }
.two { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
@media (max-width:800px) { .two { grid-template-columns:1fr; } }
details summary { cursor:pointer; color:var(--muted); }
.lim { white-space:pre-wrap; }
</style>
</head>
<body>
<main>
<h1>OYSTER results</h1>
<p class="sub">Orchestration with Your Success metrics, Transparent Evaluation &amp; Routing. Three review strategies as paths through one graph, priced, run and scored by the same code on a seeded-bug corpus.</p>

<div class="card" id="runcard">
  <label class="small">Run <select id="run"></select></label>
  <div id="runmeta" class="small"></div>
</div>

<h2>The table</h2>
<div class="card grid"><table id="summary"></table></div>
<p class="small">Strict: finding overlaps the seeded range and names the same category. Loose: overlap only. $/bug is total dollars over strict catches, n/a when nothing was caught. Dollars are computed from the provider's token counts at the rates in the run header; a "conversation" run means counts were estimated from characters.</p>

<h2>Selection: predicted versus measured</h2>
<div class="card">
  <div class="controls">
    <label>Budget per case, $ <output id="budgetv"></output><input type="range" id="budget" min="0" max="0.02" step="0.0005"></label>
    <label>Latency tolerance, s <output id="latv"></output><input type="range" id="lat" min="0" max="300" step="5"></label>
    <label>Human cost per missed bug, $ <output id="hv"></output><input type="range" id="h" min="0" max="200" step="1"></label>
  </div>
  <div class="grid" style="margin-top:12px"><table id="select"></table></div>
  <p class="small" id="selectnote"></p>
</div>

<h2>Per case</h2>
<div class="card grid"><table id="matrix" class="matrix"></table></div>
<div class="card" id="detail"><p class="small">Click a case row to see the diff, the seeded bugs and what every node of every path returned.</p></div>

<h2>Limitations</h2>
<div class="card lim" id="limitations"></div>
<p class="small">Built <span id="built"></span>. Every number above is traceable to a retained result in <code>results/&lt;run&gt;/results.json</code> and the fixture holding the model's verbatim reply.</p>
</main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const $ = (id) => document.getElementById(id);
const fmt$ = (x) => '$' + x.toFixed(4);
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const CATS = ['logic', 'security', 'style'];
let run = D.runs[0];

function perPath(run) {
  const out = {};
  const reports = {};
  run.reports.forEach(r => reports[r.path_id + '|' + r.case_id] = r);
  for (const res of run.results) {
    const row = out[res.path_id] ||= {dollars:0, lat:[], strict:0, loose:0, seeded:0, fps:0, halted:0, parse:0, missed:0};
    row.dollars += res.cost.dollars; row.lat.push(res.cost.latency_s);
    row.halted += res.halted_reason ? 1 : 0;
    row.parse += res.node_results.filter(n => n.parse_failed).length;
    const rep = reports[res.path_id + '|' + res.case_id];
    row.strict += rep.caught_strict.length; row.loose += rep.caught_loose.length;
    row.seeded += rep.caught_loose.length + rep.missed.length; row.missed += rep.missed.length; row.fps += rep.false_positives;
  }
  return out;
}
const median = (a) => { if (!a.length) return null; const s=[...a].sort((x,y)=>x-y); const m=s.length>>1; return s.length%2? s[m] : (s[m-1]+s[m])/2; };
const pathById = {}; D.paths.forEach(p => pathById[p.id] = p);
const caseById = {}; D.cases.forEach(c => caseById[c.id] = c);

function priorsMaps(run) {
  const cr = {}, mc = {};
  (run.priors.catch_rate || []).forEach(e => cr[e.role + '|' + e.model_alias + '|' + e.category] = e.rate);
  (run.priors.mean_cost || []).forEach(e => mc[e.role + '|' + e.model_alias] = {dollars: e.dollars, latency_s: e.latency_s});
  return {cr, mc};
}
function predict(path, pm) {
  let dollars = 0, lat = 0, hasPriors = true;
  for (const n of path.nodes) { const c = pm.mc[n.role + '|' + n.model_alias]; if (!c) { hasPriors = false; continue; } dollars += c.dollars; lat += c.latency_s; }
  let q = 0;
  for (const cat of CATS) { let miss = 1; for (const n of path.nodes) miss *= 1 - (pm.cr[n.role + '|' + n.model_alias + '|' + cat] || 0); q += 1 - miss; }
  return {quality: q / CATS.length, dollars, lat, hasPriors};
}

function renderRunMeta() {
  const m = run.models || {};
  const models = Object.entries(m).map(([k, v]) => `${k} = ${v.model_id} @ $${v.rate_in}/$${v.rate_out} per 1M`).join(' · ');
  $('runmeta').innerHTML = `Provider: <b>${esc(run.provider || run.name)}</b><br>${esc(models)}<br>Corpus: ${esc(run.corpus_line || '')}`;
}

function renderSummary() {
  const pp = perPath(run);
  const maxD = Math.max(...Object.values(pp).map(r => r.dollars), 1e-9);
  let html = '<tr><th>path</th><th>description</th><th class="num">$ total</th><th class="num">strict</th><th class="num">loose</th><th class="num">seeded</th><th class="num">$/bug (strict)</th><th class="num">false pos</th><th class="num">p50 latency</th><th class="num">halted</th></tr>';
  for (const p of D.paths) {
    const r = pp[p.id]; if (!r) continue;
    const perBug = r.strict ? fmt$(r.dollars / r.strict) : 'n/a';
    const p50 = median(r.lat); const lat = p50 === null ? 'n/a' : (p50 > 0 ? p50.toFixed(2) + 's' : 'n/a');
    html += `<tr><td><b>${p.id}</b></td><td>${esc(p.description)}</td><td class="num bar"><span class="fill" style="width:${(r.dollars/maxD*100).toFixed(1)}%"></span><span class="txt">${fmt$(r.dollars)}</span></td><td class="num bar"><span class="fill" style="width:${(r.strict/r.seeded*100).toFixed(1)}%"></span><span class="txt">${r.strict}</span></td><td class="num">${r.loose}</td><td class="num">${r.seeded}</td><td class="num">${perBug}</td><td class="num">${r.fps}</td><td class="num">${lat}</td><td class="num">${r.halted}</td></tr>`;
  }
  $('summary').innerHTML = html;
}

function renderSelect() {
  const pm = priorsMaps(run); const pp = perPath(run);
  const nCases = D.cases.length || 1;
  const budget = parseFloat($('budget').value), tol = parseFloat($('lat').value), h = parseFloat($('h').value);
  $('budgetv').value = fmt$(budget); $('latv').value = tol.toFixed(0); $('hv').value = '$' + h.toFixed(0);
  const rows = D.paths.map(p => {
    const pr = predict(p, pm); const r = pp[p.id] || {dollars:0, missed:0, strict:0, seeded:0};
    let reason = null;
    if (!pr.hasPriors) reason = 'no priors'; else if (pr.lat > tol) reason = 'latency'; else if (pr.dollars > budget) reason = 'budget';
    const total = r.dollars + h * r.missed;
    return {p, pr, r, reason, total};
  });
  const feasible = rows.filter(x => !x.reason);
  let picked = null;
  if (feasible.length) picked = feasible.slice().sort((a, b) => (b.pr.quality - a.pr.quality) || (a.pr.dollars - b.pr.dollars) || a.p.id.localeCompare(b.p.id))[0];
  const bestMeasured = rows.slice().sort((a, b) => (a.total - b.total) || (b.r.strict - a.r.strict))[0];
  let html = '<tr><th>path</th><th class="num">predicted $/case</th><th class="num">predicted quality</th><th>selector</th><th class="num">measured strict</th><th class="num">measured missed</th><th class="num">AI $ (run)</th><th class="num">AI $ + h × missed</th><th></th></tr>';
  for (const x of rows) {
    const sel = x.reason ? `<span class="pill bad">rejected: ${x.reason}</span>` : (picked && picked.p.id === x.p.id ? '<span class="pill ok">selected</span>' : '<span class="pill">feasible</span>');
    const best = bestMeasured && bestMeasured.p.id === x.p.id ? '<span class="pill ok">cheapest in total</span>' : '';
    html += `<tr><td><b>${x.p.id}</b></td><td class="num">${x.pr.hasPriors ? fmt$(x.pr.dollars) : 'n/a'}</td><td class="num">${x.pr.hasPriors ? x.pr.quality.toFixed(2) : 'n/a'}</td><td>${sel}</td><td class="num">${x.r.strict} / ${x.r.seeded}</td><td class="num">${x.r.missed}</td><td class="num">${fmt$(x.r.dollars)}</td><td class="num">$${x.total.toFixed(2)}</td><td>${best}</td></tr>`;
  }
  $('select').innerHTML = html;
  const msg = [];
  if (picked) msg.push(`Under the independence assumption the selector picks <b>${picked.p.id}</b> (predicted quality ${picked.pr.quality.toFixed(2)}).`);
  else msg.push('No path is feasible under these constraints; the engine would say so and name the cheapest infeasible option.');
  if (bestMeasured) msg.push(`Counting a human at $${h.toFixed(0)} per missed bug, the measured cheapest is <b>${bestMeasured.p.id}</b>.`);
  msg.push('Predicted cost is per case from calibrated mean node costs; measured columns are over the whole corpus. Style has no seeded bugs here, so it contributes 0 to every predicted quality.');
  $('selectnote').innerHTML = msg.join(' ');
}

function renderMatrix() {
  const reports = {}; run.reports.forEach(r => reports[r.path_id + '|' + r.case_id] = r);
  let html = '<tr><th>case</th><th>source</th><th class="num">seeded</th>' + D.paths.map(p => `<th class="num">${p.id}</th>`).join('') + '</tr>';
  for (const c of D.cases) {
    const src = (c.source && c.source.pr) ? `<a href="${esc(c.source.pr)}" target="_blank" rel="noopener">${esc((c.source.repo || '') + '#' + (c.source.number || ''))}</a>` : '';
    html += `<tr data-case="${esc(c.id)}"><td>${esc(c.id)}</td><td>${src}</td><td class="num">${c.seeded.length}</td>`;
    for (const p of D.paths) {
      const rep = reports[p.id + '|' + c.id];
      if (!rep) { html += '<td class="num">–</td>'; continue; }
      const n = rep.caught_strict.length, t = rep.caught_loose.length + rep.missed.length;
      html += `<td class="num ${n === t ? 'hit' : (n === 0 ? 'miss' : '')}">${n}/${t}${rep.false_positives ? ` <span class="small">+${rep.false_positives} fp</span>` : ''}</td>`;
    }
    html += '</tr>';
  }
  $('matrix').innerHTML = html;
  $('matrix').querySelectorAll('tr[data-case]').forEach(tr => tr.addEventListener('click', () => renderDetail(tr.dataset.case)));
}

function diffHtml(diff) {
  return diff.split('\n').map(l => {
    const cls = l.startsWith('+') && !l.startsWith('+++') ? 'add' : l.startsWith('-') && !l.startsWith('---') ? 'del' : l.startsWith('@@') ? 'hunk' : '';
    return cls ? `<span class="${cls}">${esc(l)}</span>` : esc(l);
  }).join('\n');
}

function renderDetail(caseId) {
  const c = caseById[caseId];
  const results = run.results.filter(r => r.case_id === caseId);
  const reports = {}; run.reports.filter(r => r.case_id === caseId).forEach(r => reports[r.path_id] = r);
  let html = `<h3 style="margin:0 0 6px">${esc(caseId)}</h3>`;
  html += '<div class="two"><div><b>Seeded bugs</b><ul>' + c.seeded.map(b => `<li><code>${esc(b.file)}:${b.line_start}-${b.line_end}</code> <span class="pill">${esc(b.category)}</span><br><span class="small">${esc(b.description)}</span></li>`).join('') + '</ul></div>';
  html += '<div><b>Per path</b>';
  for (const res of results) {
    const rep = reports[res.path_id] || {caught_strict:[], caught_loose:[], missed:[], false_positives:0};
    html += `<details ${res.path_id === 'A' ? 'open' : ''}><summary><b>${res.path_id}</b> · ${fmt$(res.cost.dollars)} · strict ${rep.caught_strict.length}, loose ${rep.caught_loose.length}, missed ${rep.missed.length}, false positives ${rep.false_positives}${res.halted_reason ? ' · halted: ' + esc(res.halted_reason) : ''}</summary>`;
    for (const n of res.node_results) {
      html += `<div style="margin:6px 0 10px 8px"><span class="pill">${esc(n.node_id)} ${esc(n.role)}</span> <span class="small">${esc(n.completion.model_id)} · in ${n.completion.input_tokens} (cached ${n.completion.cached_input_tokens}) · out ${n.completion.output_tokens}${n.parse_failed ? ' · <span class="pill bad">parse failed</span>' : ''}</span>`;
      if (!n.findings.length) html += '<div class="small">no findings</div>';
      else html += '<ul style="margin:4px 0">' + n.findings.map(f => `<li><code>${esc(f.file)}:${f.line_start}-${f.line_end}</code> <span class="pill">${esc(f.category)}</span> <span class="small">${esc(f.description)}</span></li>`).join('') + '</ul>';
      html += '</div>';
    }
    html += '</details>';
  }
  html += '</div></div>';
  html += `<details style="margin-top:10px"><summary>Diff (${c.diff.split('\n').length} lines)</summary><pre>${diffHtml(c.diff)}</pre></details>`;
  $('detail').innerHTML = html;
  $('detail').scrollIntoView({behavior:'smooth', block:'start'});
}

function init() {
  const sel = $('run');
  D.runs.forEach((r, i) => { const o = document.createElement('option'); o.value = i; o.textContent = r.name + (r.provider ? ' — ' + r.provider : ''); sel.appendChild(o); });
  sel.addEventListener('change', () => { run = D.runs[parseInt(sel.value)]; renderAll(); });
  const pp = perPath(D.runs[0] || {results:[], reports:[]});
  const maxPer = Math.max(...Object.values(pp).map(r => r.dollars / Math.max(D.cases.length, 1)), 0.001);
  $('budget').max = (maxPer * 2).toFixed(4); $('budget').step = (maxPer / 50).toFixed(5); $('budget').value = (maxPer * 2).toFixed(4);
  $('lat').value = 120; $('h').value = 50;
  ['budget', 'lat', 'h'].forEach(id => $(id).addEventListener('input', renderSelect));
  $('limitations').innerHTML = miniMarkdown(D.limitations);
  $('built').textContent = D.built;
  renderAll();
}
function miniMarkdown(text) {
  // Enough for the verbatim Limitations text: headings, bold, italics, bullet lists, paragraphs.
  const inline = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\*(.+?)\*/g, '<i>$1</i>');
  const out = []; let list = [];
  const flush = () => { if (list.length) { out.push('<ul>' + list.map(i => `<li>${i}</li>`).join('') + '</ul>'); list = []; } };
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line) { flush(); continue; }
    if (line.startsWith('### ')) { flush(); out.push(`<h3 style="margin:14px 0 6px;font-size:15px">${inline(line.slice(4))}</h3>`); }
    else if (line.startsWith('- ')) { list.push(inline(line.slice(2))); }
    else if (list.length) { list[list.length - 1] += ' ' + inline(line); }
    else { out.push(`<p style="margin:6px 0">${inline(line)}</p>`); }
  }
  flush();
  return out.join('');
}
function renderAll() { renderRunMeta(); renderSummary(); renderSelect(); renderMatrix(); }
if (!D.runs.length) { document.querySelector('main').insertAdjacentHTML('afterbegin', '<div class="card">No runs found under results/.</div>'); } else { init(); }
</script>
</body>
</html>
"""


def build(results_root: Path, corpus_dirs: Sequence[Path], out: Path) -> Path:
    data = collect(results_root, corpus_dirs)
    payload = json.dumps(data).replace("</", "<\\/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(TEMPLATE.replace("__DATA__", payload), encoding="utf-8")
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="build_site", description=__doc__)
    parser.add_argument("--results", default="results")
    parser.add_argument(
        "--corpus",
        action="append",
        default=None,
        help="case directory, repeatable; default: every tier under oyster/corpus/",
    )
    parser.add_argument("--out", default="site/index.html")
    args = parser.parse_args(argv)
    corpus = args.corpus or [
        str(d)
        for d in (Path("oyster/corpus/cases"), Path("oyster/corpus/cases-auto"))
        if d.is_dir()
    ]
    out = build(Path(args.results), [Path(d) for d in corpus], Path(args.out))
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
