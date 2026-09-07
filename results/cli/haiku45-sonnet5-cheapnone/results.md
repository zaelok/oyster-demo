# OYSTER results

Generated: 2026-09-07T01:21:52Z
Corpus: 17 cases, 21 seeded bugs, corpus commit d385daac272620a6a3b487cf1d8044d483117718
Models: cheap-model=claude-haiku-4-5 @ $1.00/$5.00 per 1M
        strong-model=claude-sonnet-5 @ $2.00/$10.00 per 1M
Provider: claude-code: claude-haiku-4-5 effort=none, claude-sonnet-5 effort=default; API-reported tokens

| path | description | $ total | strict caught | loose caught | seeded | $/bug (strict) | p50 latency | halted |
|------|-------------|---------|---------------|--------------|--------|----------------|-------------|--------|
| A | single cheap pass: cheap-scanner(cheap-model) | $0.0254 | 18 | 20 | 21 | $0.0014 | 2.77s | 0 |
| B | cascade: cheap-scanner(cheap-model) -> deep-reviewer(strong-model) | $0.1411 | 18 | 18 | 21 | $0.0078 | 7.25s | 0 |
| C | bounded iteration: deep-reviewer -> critic -> deep-reviewer (strong-model) | $0.3020 | 20 | 20 | 21 | $0.0151 | 16.67s | 0 |

## Per-case detail

### Path A

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0012 | 1.40s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0014 | 3.10s | case-coremltools-2714-b1 | case-coremltools-2714-b1 | - | 0 | - |
| case-coremltools-2736 | $0.0013 | 2.71s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0020 | 6.74s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 1 | - |
| case-flatbuffers-9081 | $0.0013 | 2.77s | - | case-flatbuffers-9081-b2 | case-flatbuffers-9081-b1 | 0 | - |
| case-gogithub-4126 | $0.0017 | 3.18s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 1 | - |
| case-gogithub-4291 | $0.0013 | 2.68s | - | case-gogithub-4291-b1 | - | 0 | - |
| case-gson-3067 | $0.0013 | 2.64s | case-gson-3067-b1 | case-gson-3067-b1 | - | 0 | - |
| case-pkl-1656 | $0.0013 | 2.49s | case-pkl-1656-b1 | case-pkl-1656-b1 | - | 0 | - |
| case-sarama-3314 | $0.0018 | 3.33s | case-sarama-3314-b1, case-sarama-3314-b2 | case-sarama-3314-b1, case-sarama-3314-b2 | - | 0 | - |
| case-sarama-3642 | $0.0013 | 2.68s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0013 | 2.76s | case-servicetalk-3554-b1 | case-servicetalk-3554-b1 | - | 0 | - |
| case-servicetalk-3587 | $0.0014 | 2.77s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0020 | 3.11s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 1 | - |
| case-swiftcollections-661 | $0.0018 | 3.32s | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | - | 0 | - |
| case-zstd-4486 | $0.0018 | 3.16s | case-zstd-4486-b1, case-zstd-4486-b2 | case-zstd-4486-b1, case-zstd-4486-b2 | - | 0 | - |
| case-zstd-4626 | $0.0013 | 2.90s | case-zstd-4626-b1 | case-zstd-4626-b1 | - | 0 | - |

### Path B

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0046 | 4.82s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0125 | 14.44s | case-coremltools-2714-b1 | case-coremltools-2714-b1 | - | 0 | - |
| case-coremltools-2736 | $0.0052 | 5.81s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0076 | 12.28s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 1 | - |
| case-flatbuffers-9081 | $0.0065 | 7.25s | - | - | case-flatbuffers-9081-b1, case-flatbuffers-9081-b2 | 1 | - |
| case-gogithub-4126 | $0.0065 | 7.14s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 1 | - |
| case-gogithub-4291 | $0.0124 | 15.34s | - | - | case-gogithub-4291-b1 | 0 | - |
| case-gson-3067 | $0.0055 | 7.06s | case-gson-3067-b1 | case-gson-3067-b1 | - | 0 | - |
| case-pkl-1656 | $0.0084 | 12.33s | case-pkl-1656-b1 | case-pkl-1656-b1 | - | 0 | - |
| case-sarama-3314 | $0.0074 | 7.98s | case-sarama-3314-b1, case-sarama-3314-b2 | case-sarama-3314-b1, case-sarama-3314-b2 | - | 0 | - |
| case-sarama-3642 | $0.0051 | 6.56s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0051 | 6.62s | case-servicetalk-3554-b1 | case-servicetalk-3554-b1 | - | 0 | - |
| case-servicetalk-3587 | $0.0057 | 6.83s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0117 | 12.14s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 0 | - |
| case-swiftcollections-661 | $0.0082 | 10.86s | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | - | 0 | - |
| case-zstd-4486 | $0.0062 | 6.30s | case-zstd-4486-b1, case-zstd-4486-b2 | case-zstd-4486-b1, case-zstd-4486-b2 | - | 0 | - |
| case-zstd-4626 | $0.0223 | 21.04s | case-zstd-4626-b1 | case-zstd-4626-b1 | - | 0 | - |

### Path C

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0108 | 9.72s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0188 | 22.45s | case-coremltools-2714-b1 | case-coremltools-2714-b1 | - | 0 | - |
| case-coremltools-2736 | $0.0117 | 16.67s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0143 | 13.50s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 0 | - |
| case-flatbuffers-9081 | $0.0210 | 24.52s | case-flatbuffers-9081-b1 | case-flatbuffers-9081-b1 | case-flatbuffers-9081-b2 | 0 | - |
| case-gogithub-4126 | $0.0115 | 11.79s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 0 | - |
| case-gogithub-4291 | $0.0335 | 38.07s | case-gogithub-4291-b1 | case-gogithub-4291-b1 | - | 0 | - |
| case-gson-3067 | $0.0180 | 18.91s | case-gson-3067-b1 | case-gson-3067-b1 | - | 0 | - |
| case-pkl-1656 | $0.0159 | 12.88s | case-pkl-1656-b1 | case-pkl-1656-b1 | - | 1 | - |
| case-sarama-3314 | $0.0244 | 22.00s | case-sarama-3314-b1, case-sarama-3314-b2 | case-sarama-3314-b1, case-sarama-3314-b2 | - | 0 | - |
| case-sarama-3642 | $0.0136 | 12.24s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0118 | 10.87s | case-servicetalk-3554-b1 | case-servicetalk-3554-b1 | - | 0 | - |
| case-servicetalk-3587 | $0.0172 | 16.29s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0237 | 33.75s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 1 | - |
| case-swiftcollections-661 | $0.0197 | 34.18s | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | - | 0 | - |
| case-zstd-4486 | $0.0141 | 12.53s | case-zstd-4486-b1, case-zstd-4486-b2 | case-zstd-4486-b1, case-zstd-4486-b2 | - | 0 | - |
| case-zstd-4626 | $0.0221 | 21.18s | case-zstd-4626-b1 | case-zstd-4626-b1 | - | 0 | - |

## Limitations

**What the numbers do and don't show**: catch-rates are corpus-specific; N is small; seeded bugs are cleaner than wild bugs. The table supports the *claim* (§0) — that selection over measured paths is possible and auditable — not a general benchmark of any model's review ability.

### Non-Goals (this slice)

- **Unbounded runtime cycles** (convergence-criterion stopping). A cyclic graph requires a termination argument — cost budget as a **variant function**, monotonically decreasing per traversal. The DAG slice guarantees finite execution structurally; the variant-function treatment for true cycles is designed (vision doc) and is v2.
- **Runtime re-planning** (switching paths mid-run on intermediate results) and **dynamic node creation** — not on the MVP critical path; both need evaluation machinery of their own.
- **Learned quality priors** (§1.4 note) and **semantic result caching** — future work, one sentence each in the README.
- **Any hosted service.** The deliverable is a reproducible repo, not a deployment.
