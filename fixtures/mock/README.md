# Mock fixtures

Recorded completions for `MockProvider`, one JSON file per request keyed by
`sha256(model_id + system + user + cached_prefix)[:16]`. `--provider anthropic` records here by
default (`--no-record` to skip), so a paid run can be replayed offline by `make eval-mock` and
by CI.

With no fixtures present every request returns `{"findings": []}`: the table is complete and
honest, and every path catches nothing.
