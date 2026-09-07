# OYSTER results

Generated: 2026-09-07T01:14:33Z
Corpus: 17 cases, 21 seeded bugs, corpus commit d385daac272620a6a3b487cf1d8044d483117718
Models: cheap-model=claude-haiku-4-5 @ $1.00/$5.00 per 1M
        strong-model=claude-sonnet-5 @ $2.00/$10.00 per 1M
Provider: claude-code

| path | description | $ total | strict caught | loose caught | seeded | $/bug (strict) | p50 latency | halted |
|------|-------------|---------|---------------|--------------|--------|----------------|-------------|--------|
| A | single cheap pass: cheap-scanner(cheap-model) | $0.5132 | 13 | 14 | 21 | $0.0395 | 45.76s | 0 |
| B | cascade: cheap-scanner(cheap-model) -> deep-reviewer(strong-model) | $0.6411 | 18 | 18 | 21 | $0.0356 | 53.31s | 0 |
| C | bounded iteration: deep-reviewer -> critic -> deep-reviewer (strong-model) | $0.3247 | 18 | 18 | 21 | $0.0180 | 14.93s | 0 |

## Per-case detail

### Path A

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0046 | 8.61s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0581 | 109.66s | case-coremltools-2714-b1 | case-coremltools-2714-b1 | - | 0 | - |
| case-coremltools-2736 | $0.0043 | 7.16s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0086 | 14.53s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 0 | - |
| case-flatbuffers-9081 | $0.0289 | 53.29s | - | case-flatbuffers-9081-b1 | case-flatbuffers-9081-b2 | 0 | - |
| case-gogithub-4126 | $0.0274 | 49.47s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 0 | - |
| case-gogithub-4291 | $0.0364 | 56.89s | - | - | case-gogithub-4291-b1 | 0 | - |
| case-gson-3067 | $0.0250 | 50.62s | - | - | case-gson-3067-b1 | 0 | - |
| case-pkl-1656 | $0.1042 | 187.76s | - | - | case-pkl-1656-b1 | 1 | - |
| case-sarama-3314 | $0.0484 | 61.01s | case-sarama-3314-b1, case-sarama-3314-b2 | case-sarama-3314-b1, case-sarama-3314-b2 | - | 0 | - |
| case-sarama-3642 | $0.0066 | 9.81s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0105 | 18.81s | - | - | case-servicetalk-3554-b1 | 1 | - |
| case-servicetalk-3587 | $0.0150 | 28.75s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0163 | 32.95s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 0 | - |
| case-swiftcollections-661 | $0.0102 | 15.35s | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | - | 0 | - |
| case-zstd-4486 | $0.0730 | 134.87s | - | - | case-zstd-4486-b1, case-zstd-4486-b2 | 2 | - |
| case-zstd-4626 | $0.0357 | 45.76s | case-zstd-4626-b1 | case-zstd-4626-b1 | - | 0 | - |

### Path B

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0078 | 12.31s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0775 | 130.25s | case-coremltools-2714-b1 | case-coremltools-2714-b1 | - | 0 | - |
| case-coremltools-2736 | $0.0084 | 11.20s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0129 | 18.42s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 0 | - |
| case-flatbuffers-9081 | $0.0334 | 57.47s | - | - | case-flatbuffers-9081-b1, case-flatbuffers-9081-b2 | 1 | - |
| case-gogithub-4126 | $0.0311 | 53.31s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 0 | - |
| case-gogithub-4291 | $0.0578 | 75.53s | case-gogithub-4291-b1 | case-gogithub-4291-b1 | - | 0 | - |
| case-gson-3067 | $0.0303 | 56.83s | - | - | case-gson-3067-b1 | 0 | - |
| case-pkl-1656 | $0.1099 | 192.08s | case-pkl-1656-b1 | case-pkl-1656-b1 | - | 1 | - |
| case-sarama-3314 | $0.0539 | 65.89s | case-sarama-3314-b1, case-sarama-3314-b2 | case-sarama-3314-b1, case-sarama-3314-b2 | - | 0 | - |
| case-sarama-3642 | $0.0102 | 13.38s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0147 | 22.66s | case-servicetalk-3554-b1 | case-servicetalk-3554-b1 | - | 0 | - |
| case-servicetalk-3587 | $0.0198 | 32.83s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0268 | 41.84s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 0 | - |
| case-swiftcollections-661 | $0.0166 | 21.27s | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | - | 0 | - |
| case-zstd-4486 | $0.0783 | 139.31s | case-zstd-4486-b1, case-zstd-4486-b2 | case-zstd-4486-b1, case-zstd-4486-b2 | - | 0 | - |
| case-zstd-4626 | $0.0519 | 60.03s | case-zstd-4626-b1 | case-zstd-4626-b1 | - | 0 | - |

### Path C

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0111 | 10.74s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0169 | 16.85s | case-coremltools-2714-b1 | case-coremltools-2714-b1 | - | 0 | - |
| case-coremltools-2736 | $0.0115 | 12.00s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0191 | 18.75s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 0 | - |
| case-flatbuffers-9081 | $0.0236 | 25.65s | - | - | case-flatbuffers-9081-b1, case-flatbuffers-9081-b2 | 2 | - |
| case-gogithub-4126 | $0.0111 | 9.62s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 0 | - |
| case-gogithub-4291 | $0.0503 | 50.74s | case-gogithub-4291-b1 | case-gogithub-4291-b1 | - | 0 | - |
| case-gson-3067 | $0.0120 | 14.69s | - | - | case-gson-3067-b1 | 0 | - |
| case-pkl-1656 | $0.0293 | 24.93s | case-pkl-1656-b1 | case-pkl-1656-b1 | - | 0 | - |
| case-sarama-3314 | $0.0195 | 23.66s | case-sarama-3314-b1, case-sarama-3314-b2 | case-sarama-3314-b1, case-sarama-3314-b2 | - | 0 | - |
| case-sarama-3642 | $0.0131 | 12.62s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0127 | 12.89s | case-servicetalk-3554-b1 | case-servicetalk-3554-b1 | - | 0 | - |
| case-servicetalk-3587 | $0.0147 | 13.61s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0235 | 21.36s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 0 | - |
| case-swiftcollections-661 | $0.0222 | 19.35s | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | - | 0 | - |
| case-zstd-4486 | $0.0153 | 11.26s | case-zstd-4486-b1, case-zstd-4486-b2 | case-zstd-4486-b1, case-zstd-4486-b2 | - | 0 | - |
| case-zstd-4626 | $0.0189 | 14.93s | case-zstd-4626-b1 | case-zstd-4626-b1 | - | 0 | - |

## Limitations

**What the numbers do and don't show**: catch-rates are corpus-specific; N is small; seeded bugs are cleaner than wild bugs. The table supports the *claim* (§0) — that selection over measured paths is possible and auditable — not a general benchmark of any model's review ability.

### Non-Goals (this slice)

- **Unbounded runtime cycles** (convergence-criterion stopping). A cyclic graph requires a termination argument — cost budget as a **variant function**, monotonically decreasing per traversal. The DAG slice guarantees finite execution structurally; the variant-function treatment for true cycles is designed (vision doc) and is v2.
- **Runtime re-planning** (switching paths mid-run on intermediate results) and **dynamic node creation** — not on the MVP critical path; both need evaluation machinery of their own.
- **Learned quality priors** (§1.4 note) and **semantic result caching** — future work, one sentence each in the README.
- **Any hosted service.** The deliverable is a reproducible repo, not a deployment.
