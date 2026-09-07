# Corpus sources

Every case is a merged bug-fix PR from a public repository, reversed so the fixed code is the before side and the buggy code the after side (`tools/pr_to_case.py`). All PRs merged after September 2025. Seeded labels were reviewed by hand; the description states what is wrong, not what was fixed.

| case | source PR | category | seeded |
|---|---|---|---|
| case-servicetalk-3554 | https://github.com/apple/servicetalk/pull/3554 | logic | 1 |
| case-servicetalk-3587 | https://github.com/apple/servicetalk/pull/3587 | logic | 1 |
| case-servicetalk-3588 | https://github.com/apple/servicetalk/pull/3588 | logic | 1 |
| case-pkl-1656 | https://github.com/apple/pkl/pull/1656 | logic | 1 |
| case-coremltools-2736 | https://github.com/apple/coremltools/pull/2736 | logic | 1 |
| case-coremltools-2714 | https://github.com/apple/coremltools/pull/2714 | logic | 1 |
| case-swiftcollections-661 | https://github.com/apple/swift-collections/pull/661 | logic | 2 |
| case-sarama-3642 | https://github.com/IBM/sarama/pull/3642 | logic | 1 |
| case-sarama-3314 | https://github.com/IBM/sarama/pull/3314 | logic | 2 |
| case-gson-3067 | https://github.com/google/gson/pull/3067 | logic | 1 |
| case-gogithub-4291 | https://github.com/google/go-github/pull/4291 | security | 1 |
| case-gogithub-4126 | https://github.com/google/go-github/pull/4126 | security | 1 |
| case-flatbuffers-9081 | https://github.com/google/flatbuffers/pull/9081 | security | 2 |
| case-errorprone-5603 | https://github.com/google/error-prone/pull/5603 | logic | 1 |
| case-adk-5415 | https://github.com/google/adk-python/pull/5415 | logic | 1 |
| case-zstd-4626 | https://github.com/facebook/zstd/pull/4626 | logic | 1 |
| case-zstd-4486 | https://github.com/facebook/zstd/pull/4486 | logic | 2 |

17 cases, 21 seeded bugs.

## Licensing of the excerpts

Each case embeds a short excerpt (the reversed hunks of one merged pull request) from the
repository linked in its row. Those excerpts remain under their original licenses (Apache-2.0,
BSD-3-Clause and MIT across the sources above) and their copyright stays with their authors;
`THIRD-PARTY-NOTICES.md` at the repository root names each source repository's license and reproduces the license texts, and the link is the attribution to the change. The repository's own license covers the engine, the tooling and
the labels, not the excerpts.
