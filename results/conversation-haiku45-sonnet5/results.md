# OYSTER results

Generated: 2026-09-06T18:46:37Z
Corpus: 17 cases, 21 seeded bugs, corpus commit cba004d1e03e51be3714943e7b4032e41b6193a4
Models: cheap-model=claude-haiku-4-5 @ $1.00/$5.00 per 1M
        strong-model=claude-sonnet-5 @ $2.00/$10.00 per 1M
Provider: conversation: claude.ai Haiku 4.5 (no extended) + Sonnet 5 (medium), estimated tokens

| path | description | $ total | strict caught | loose caught | seeded | $/bug (strict) | p50 latency | halted |
|------|-------------|---------|---------------|--------------|--------|----------------|-------------|--------|
| A | single cheap pass: cheap-scanner(cheap-model) | $0.0120 | 15 | 15 | 21 | $0.0008 | 0.00s | 0 |
| B | cascade: cheap-scanner(cheap-model) -> deep-reviewer(strong-model) | $0.0446 | 16 | 16 | 21 | $0.0028 | 0.00s | 0 |
| C | bounded iteration: deep-reviewer -> critic -> deep-reviewer (strong-model) | $0.0975 | 14 | 14 | 21 | $0.0070 | 0.00s | 0 |

## Per-case detail

### Path A

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0007 | 0.00s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0007 | 0.00s | case-coremltools-2714-b1 | case-coremltools-2714-b1 | - | 0 | - |
| case-coremltools-2736 | $0.0007 | 0.00s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0008 | 0.00s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 0 | - |
| case-flatbuffers-9081 | $0.0007 | 0.00s | - | - | case-flatbuffers-9081-b1, case-flatbuffers-9081-b2 | 1 | - |
| case-gogithub-4126 | $0.0007 | 0.00s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 0 | - |
| case-gogithub-4291 | $0.0004 | 0.00s | - | - | case-gogithub-4291-b1 | 0 | - |
| case-gson-3067 | $0.0003 | 0.00s | - | - | case-gson-3067-b1 | 0 | - |
| case-pkl-1656 | $0.0007 | 0.00s | case-pkl-1656-b1 | case-pkl-1656-b1 | - | 0 | - |
| case-sarama-3314 | $0.0006 | 0.00s | case-sarama-3314-b2 | case-sarama-3314-b2 | case-sarama-3314-b1 | 0 | - |
| case-sarama-3642 | $0.0006 | 0.00s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0007 | 0.00s | case-servicetalk-3554-b1 | case-servicetalk-3554-b1 | - | 0 | - |
| case-servicetalk-3587 | $0.0008 | 0.00s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0008 | 0.00s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 0 | - |
| case-swiftcollections-661 | $0.0010 | 0.00s | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | - | 0 | - |
| case-zstd-4486 | $0.0010 | 0.00s | case-zstd-4486-b1 | case-zstd-4486-b1 | case-zstd-4486-b2 | 1 | - |
| case-zstd-4626 | $0.0007 | 0.00s | case-zstd-4626-b1 | case-zstd-4626-b1 | - | 0 | - |

### Path B

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0024 | 0.00s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0026 | 0.00s | case-coremltools-2714-b1 | case-coremltools-2714-b1 | - | 0 | - |
| case-coremltools-2736 | $0.0028 | 0.00s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0030 | 0.00s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 0 | - |
| case-flatbuffers-9081 | $0.0030 | 0.00s | case-flatbuffers-9081-b1 | case-flatbuffers-9081-b1 | case-flatbuffers-9081-b2 | 0 | - |
| case-gogithub-4126 | $0.0025 | 0.00s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 0 | - |
| case-gogithub-4291 | $0.0011 | 0.00s | - | - | case-gogithub-4291-b1 | 0 | - |
| case-gson-3067 | $0.0010 | 0.00s | - | - | case-gson-3067-b1 | 0 | - |
| case-pkl-1656 | $0.0031 | 0.00s | case-pkl-1656-b1 | case-pkl-1656-b1 | - | 0 | - |
| case-sarama-3314 | $0.0031 | 0.00s | case-sarama-3314-b1 | case-sarama-3314-b1 | case-sarama-3314-b2 | 1 | - |
| case-sarama-3642 | $0.0022 | 0.00s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0025 | 0.00s | case-servicetalk-3554-b1 | case-servicetalk-3554-b1 | - | 0 | - |
| case-servicetalk-3587 | $0.0027 | 0.00s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0030 | 0.00s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 0 | - |
| case-swiftcollections-661 | $0.0037 | 0.00s | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | case-swiftcollections-661-b1, case-swiftcollections-661-b2 | - | 0 | - |
| case-zstd-4486 | $0.0034 | 0.00s | case-zstd-4486-b1 | case-zstd-4486-b1 | case-zstd-4486-b2 | 1 | - |
| case-zstd-4626 | $0.0026 | 0.00s | case-zstd-4626-b1 | case-zstd-4626-b1 | - | 0 | - |

### Path C

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-adk-5415 | $0.0051 | 0.00s | case-adk-5415-b1 | case-adk-5415-b1 | - | 0 | - |
| case-coremltools-2714 | $0.0061 | 0.00s | - | - | case-coremltools-2714-b1 | 1 | - |
| case-coremltools-2736 | $0.0062 | 0.00s | case-coremltools-2736-b1 | case-coremltools-2736-b1 | - | 0 | - |
| case-errorprone-5603 | $0.0071 | 0.00s | case-errorprone-5603-b1 | case-errorprone-5603-b1 | - | 0 | - |
| case-flatbuffers-9081 | $0.0068 | 0.00s | case-flatbuffers-9081-b1 | case-flatbuffers-9081-b1 | case-flatbuffers-9081-b2 | 0 | - |
| case-gogithub-4126 | $0.0055 | 0.00s | case-gogithub-4126-b1 | case-gogithub-4126-b1 | - | 0 | - |
| case-gogithub-4291 | $0.0021 | 0.00s | - | - | case-gogithub-4291-b1 | 0 | - |
| case-gson-3067 | $0.0045 | 0.00s | case-gson-3067-b1 | case-gson-3067-b1 | - | 0 | - |
| case-pkl-1656 | $0.0061 | 0.00s | case-pkl-1656-b1 | case-pkl-1656-b1 | - | 0 | - |
| case-sarama-3314 | $0.0064 | 0.00s | case-sarama-3314-b2 | case-sarama-3314-b2 | case-sarama-3314-b1 | 0 | - |
| case-sarama-3642 | $0.0057 | 0.00s | case-sarama-3642-b1 | case-sarama-3642-b1 | - | 0 | - |
| case-servicetalk-3554 | $0.0053 | 0.00s | case-servicetalk-3554-b1 | case-servicetalk-3554-b1 | - | 0 | - |
| case-servicetalk-3587 | $0.0067 | 0.00s | case-servicetalk-3587-b1 | case-servicetalk-3587-b1 | - | 0 | - |
| case-servicetalk-3588 | $0.0072 | 0.00s | case-servicetalk-3588-b1 | case-servicetalk-3588-b1 | - | 0 | - |
| case-swiftcollections-661 | $0.0063 | 0.00s | case-swiftcollections-661-b1 | case-swiftcollections-661-b1 | case-swiftcollections-661-b2 | 0 | - |
| case-zstd-4486 | $0.0058 | 0.00s | case-zstd-4486-b1 | case-zstd-4486-b1 | case-zstd-4486-b2 | 0 | - |
| case-zstd-4626 | $0.0048 | 0.00s | - | - | case-zstd-4626-b1 | 1 | - |

## Limitations

**What the numbers do and don't show**: catch-rates are corpus-specific; N is small; seeded bugs are cleaner than wild bugs. The table supports the *claim* (§0) — that selection over measured paths is possible and auditable — not a general benchmark of any model's review ability.

### Non-Goals (this slice)

- **Unbounded runtime cycles** (convergence-criterion stopping). A cyclic graph requires a termination argument — cost budget as a **variant function**, monotonically decreasing per traversal. The DAG slice guarantees finite execution structurally; the variant-function treatment for true cycles is designed (vision doc) and is v2.
- **Runtime re-planning** (switching paths mid-run on intermediate results) and **dynamic node creation** — not on the MVP critical path; both need evaluation machinery of their own.
- **Learned quality priors** (§1.4 note) and **semantic result caching** — future work, one sentence each in the README.
- **Any hosted service.** The deliverable is a reproducible repo, not a deployment.
