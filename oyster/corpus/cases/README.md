# Corpus cases

**Cases are human authored.** Agents never write files in this directory. The seeded bugs are
the ground truth every number in `results.md` is measured against, so they stay under human
control (build spec §9, wave 4).

One JSON file per case. The filename stem must equal the case `id`.

```json
{
  "id": "case-01",
  "diff": "--- a/pricing.py\n+++ b/pricing.py\n@@ -10,7 +10,7 @@\n...",
  "seeded": [
    {"id": "case-01-b1", "file": "pricing.py", "line_start": 42, "line_end": 44,
     "category": "logic", "description": "off-by-one in the discount tier boundary"}
  ]
}
```

Validation rules (the loader refuses anything that fails one, naming the case and field):

1. `id` is unique across the corpus and matches the filename stem
2. `diff` is non-empty and is a unified diff with at least one hunk
3. every `seeded[].file` appears as a target path (`+++ b/<file>`) in the diff
4. every `seeded[].line_start <= line_end`, both positive
5. every seeded line range falls inside a hunk on the new-file side
6. `category` is one of `logic`, `security`, `style`
7. seeded bug ids are unique within the case

Line numbers are new-file side. Keep the diffs small (a few hunks) and seed bugs across all
three categories so the calibration pass has something to measure in each. See
`_example.json.template` for a starting point and `tests/fixtures/corpus/case-01.json` for a
complete, valid example.
