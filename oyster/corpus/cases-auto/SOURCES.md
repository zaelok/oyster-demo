# Corpus sources: auto tier

Every case is a merged bug-fix PR from a public repository, reversed by `tools/build_corpus.py` so the fixed code is the before side and the buggy code the after side. All PRs merged on or after 2025-09-01. **Nobody reviewed these labels.** The seeded range is where the fix changed code; the description is the PR title; the category is a keyword guess. See README.md in this directory for what that means.

| case | source PR | merged | language | category | seeded | kinds |
|---|---|---|---|---|---|---|
| case-anthropicsdkcsharp-236 | https://github.com/anthropics/anthropic-sdk-csharp/pull/236 | 2026-08-11 | csharp | logic | 1 | deletion-only |
| case-anthropicsdkjava-295 | https://github.com/anthropics/anthropic-sdk-java/pull/295 | 2026-01-07 | kotlin | logic | 1 | added |
| case-anthropicsdkjava-309 | https://github.com/anthropics/anthropic-sdk-java/pull/309 | 2026-03-09 | kotlin | logic | 2 | deletion-only, added |
| case-anthropicsdkjava-382 | https://github.com/anthropics/anthropic-sdk-java/pull/382 | 2026-08-11 | kotlin | logic | 2 | added, added |
| case-anthropicsdkpython-1124 | https://github.com/anthropics/anthropic-sdk-python/pull/1124 | 2026-03-02 | python | logic | 1 | added |
| case-anthropicsdkpython-1244 | https://github.com/anthropics/anthropic-sdk-python/pull/1244 | 2026-03-16 | python | logic | 2 | deletion-only, deletion-only |
| case-anthropicsdkpython-1275 | https://github.com/anthropics/anthropic-sdk-python/pull/1275 | 2026-03-20 | python | logic | 1 | deletion-only |
| case-anthropicsdkpython-1642 | https://github.com/anthropics/anthropic-sdk-python/pull/1642 | 2026-06-04 | python | logic | 2 | added, deletion-only |
| case-anthropicsdkruby-124 | https://github.com/anthropics/anthropic-sdk-ruby/pull/124 | 2025-09-04 | ruby | logic | 1 | added |
| case-anthropicsdkruby-126 | https://github.com/anthropics/anthropic-sdk-ruby/pull/126 | 2025-09-29 | ruby | logic | 2 | added, added |
| case-anthropicsdkruby-189 | https://github.com/anthropics/anthropic-sdk-ruby/pull/189 | 2026-05-11 | ruby | logic | 1 | added |
| case-anthropicsdktypescript-1021 | https://github.com/anthropics/anthropic-sdk-typescript/pull/1021 | 2026-04-30 | typescript | logic | 3 | deletion-only, added, deletion-only |
| case-anthropicsdktypescript-856 | https://github.com/anthropics/anthropic-sdk-typescript/pull/856 | 2025-12-05 | typescript | logic | 2 | deletion-only, deletion-only |
| case-apex-2018 | https://github.com/NVIDIA/apex/pull/2018 | 2026-08-27 | c | logic | 3 | added, deletion-only, deletion-only |
| case-beakergantry-185 | https://github.com/allenai/beaker-gantry/pull/185 | 2026-03-07 | python | logic | 2 | added, deletion-only |
| case-cccl-11103 | https://github.com/NVIDIA/cccl/pull/11103 | 2026-09-02 | c | logic | 1 | added |
| case-cccl-11176 | https://github.com/NVIDIA/cccl/pull/11176 | 2026-09-03 | c | logic | 1 | added |
| case-claudeagentsdkpython-1058 | https://github.com/anthropics/claude-agent-sdk-python/pull/1058 | 2026-06-26 | python | logic | 3 | deletion-only, deletion-only, added |
| case-claudecodeaction-1692 | https://github.com/anthropics/claude-code-action/pull/1692 | 2026-08-19 | typescript | security | 1 | deletion-only |
| case-codex-4944 | https://github.com/openai/codex/pull/4944 | 2025-10-08 | rust | logic | 3 | deletion-only, added, deletion-only |
| case-codex-4967 | https://github.com/openai/codex/pull/4967 | 2025-10-08 | rust | logic | 2 | added, added |
| case-codex-4992 | https://github.com/openai/codex/pull/4992 | 2025-10-09 | rust | logic | 1 | added |
| case-codex-5016 | https://github.com/openai/codex/pull/5016 | 2025-10-09 | rust | logic | 2 | added, deletion-only |
| case-codex-5069 | https://github.com/openai/codex/pull/5069 | 2025-10-28 | rust | logic | 2 | added, deletion-only |
| case-container-2138 | https://github.com/apple/container/pull/2138 | 2026-08-27 | swift | security | 1 | deletion-only |
| case-containerization-794 | https://github.com/apple/containerization/pull/794 | 2026-07-07 | swift | logic | 1 | deletion-only |
| case-containerization-833 | https://github.com/apple/containerization/pull/833 | 2026-08-06 | swift | logic | 3 | deletion-only, added, added |
| case-containerization-856 | https://github.com/apple/containerization/pull/856 | 2026-08-27 | swift | logic | 1 | added |
| case-coremltools-2770 | https://github.com/apple/coremltools/pull/2770 | 2026-08-25 | python | logic | 1 | deletion-only |
| case-coremltools-2771 | https://github.com/apple/coremltools/pull/2771 | 2026-08-05 | python | logic | 3 | deletion-only, added, added |
| case-coremltools-2774 | https://github.com/apple/coremltools/pull/2774 | 2026-08-06 | python | logic | 2 | deletion-only, added |
| case-coremltools-2778 | https://github.com/apple/coremltools/pull/2778 | 2026-08-06 | python | logic | 1 | added |
| case-cudapython-2739 | https://github.com/NVIDIA/cuda-python/pull/2739 | 2026-08-31 | python | logic | 1 | added |
| case-cudf-23973 | https://github.com/NVIDIA/cudf/pull/23973 | 2026-09-04 | cuda | logic | 3 | deletion-only, deletion-only, added |
| case-cudfspark-15870 | https://github.com/NVIDIA/cudf-spark/pull/15870 | 2026-09-03 | python | logic | 2 | deletion-only, added |
| case-cudfspark-15900 | https://github.com/NVIDIA/cudf-spark/pull/15900 | 2026-09-05 | scala | security | 2 | added, added |
| case-cugraph-5632 | https://github.com/rapidsai/cugraph/pull/5632 | 2026-08-19 | cpp | logic | 2 | added, added |
| case-cuopt-1834 | https://github.com/NVIDIA/cuopt/pull/1834 | 2026-09-01 | cpp | logic | 3 | added, added, added |
| case-cupy-10273 | https://github.com/cupy/cupy/pull/10273 | 2026-09-05 | python | logic | 1 | added |
| case-cutlass-3427 | https://github.com/NVIDIA/cutlass/pull/3427 | 2026-08-06 | cpp | logic | 3 | added, deletion-only, added |
| case-cutlass-3461 | https://github.com/NVIDIA/cutlass/pull/3461 | 2026-08-14 | python | logic | 2 | added, added |
| case-cutlass-3464 | https://github.com/NVIDIA/cutlass/pull/3464 | 2026-08-20 | python | logic | 1 | deletion-only |
| case-cuvs-2513 | https://github.com/NVIDIA/cuvs/pull/2513 | 2026-09-03 | cpp | logic | 3 | added, added, deletion-only |
| case-dali-6422 | https://github.com/NVIDIA/DALI/pull/6422 | 2026-07-15 | python | logic | 1 | added |
| case-dali-6458 | https://github.com/NVIDIA/DALI/pull/6458 | 2026-08-26 | python | logic | 1 | added |
| case-flashattention-178 | https://github.com/vllm-project/flash-attention/pull/178 | 2026-08-12 | python | logic | 3 | deletion-only, deletion-only, deletion-only |
| case-flashattention-192 | https://github.com/vllm-project/flash-attention/pull/192 | 2026-09-01 | python | logic | 3 | deletion-only, deletion-only, added |
| case-flashattention-2787 | https://github.com/Dao-AILab/flash-attention/pull/2787 | 2026-08-11 | python | logic | 3 | added, added, added |
| case-gosdk-1176 | https://github.com/modelcontextprotocol/go-sdk/pull/1176 | 2026-08-17 | go | logic | 2 | deletion-only, added |
| case-gosdk-1184 | https://github.com/modelcontextprotocol/go-sdk/pull/1184 | 2026-08-21 | go | logic | 2 | deletion-only, added |
| case-gosdk-1221 | https://github.com/modelcontextprotocol/go-sdk/pull/1221 | 2026-09-01 | go | logic | 3 | added, added, added |
| case-gptoss-163 | https://github.com/openai/gpt-oss/pull/163 | 2025-09-02 | c | logic | 2 | deletion-only, added |
| case-gptoss-182 | https://github.com/openai/gpt-oss/pull/182 | 2025-09-15 | python | logic | 1 | added |
| case-gptoss-194 | https://github.com/openai/gpt-oss/pull/194 | 2025-09-22 | c | logic | 1 | deletion-only |
| case-gptoss-250 | https://github.com/openai/gpt-oss/pull/250 | 2026-07-24 | python | security | 3 | deletion-only, added, added |
| case-gpuoperator-2792 | https://github.com/NVIDIA/gpu-operator/pull/2792 | 2026-08-26 | go | security | 3 | deletion-only, added, added |
| case-guidellm-1072 | https://github.com/vllm-project/guidellm/pull/1072 | 2026-09-01 | python | logic | 3 | added, added, added |
| case-inspector-2267 | https://github.com/modelcontextprotocol/inspector/pull/2267 | 2026-09-06 | typescript | logic | 2 | added, added |
| case-javasdk-1104 | https://github.com/modelcontextprotocol/java-sdk/pull/1104 | 2026-08-26 | java | logic | 1 | added |
| case-javasdk-1109 | https://github.com/modelcontextprotocol/java-sdk/pull/1109 | 2026-08-26 | java | logic | 1 | added |
| case-k8sdeviceplugin-1928 | https://github.com/NVIDIA/k8s-device-plugin/pull/1928 | 2026-08-26 | go | logic | 2 | deletion-only, added |
| case-k8sdeviceplugin-1995 | https://github.com/NVIDIA/k8s-device-plugin/pull/1995 | 2026-09-01 | go | logic | 3 | added, added, added |
| case-kotlinsdk-912 | https://github.com/modelcontextprotocol/kotlin-sdk/pull/912 | 2026-07-28 | kotlin | logic | 1 | added |
| case-kvikio-990 | https://github.com/rapidsai/kvikio/pull/990 | 2026-06-24 | cpp | logic | 1 | added |
| case-litellm-39780 | https://github.com/BerriAI/litellm/pull/39780 | 2026-09-05 | python | logic | 3 | deletion-only, deletion-only, added |
| case-litellm-39815 | https://github.com/BerriAI/litellm/pull/39815 | 2026-09-05 | python | logic | 2 | added, added |
| case-litellm-39848 | https://github.com/BerriAI/litellm/pull/39848 | 2026-09-05 | python | security | 1 | deletion-only |
| case-litellm-39871 | https://github.com/BerriAI/litellm/pull/39871 | 2026-09-05 | python | security | 1 | added |
| case-litellm-39873 | https://github.com/BerriAI/litellm/pull/39873 | 2026-09-05 | python | logic | 2 | added, added |
| case-litellm-39955 | https://github.com/BerriAI/litellm/pull/39955 | 2026-09-06 | python | logic | 2 | added, added |
| case-litellm-39960 | https://github.com/BerriAI/litellm/pull/39960 | 2026-09-05 | python | security | 2 | added, added |
| case-litellm-39964 | https://github.com/BerriAI/litellm/pull/39964 | 2026-09-05 | python | security | 3 | added, deletion-only, added |
| case-litellm-39972 | https://github.com/BerriAI/litellm/pull/39972 | 2026-09-06 | python | logic | 1 | added |
| case-llmcompressor-3070 | https://github.com/vllm-project/llm-compressor/pull/3070 | 2026-08-26 | python | logic | 1 | added |
| case-llmcompressor-3079 | https://github.com/vllm-project/llm-compressor/pull/3079 | 2026-08-23 | python | logic | 2 | added, added |
| case-llmcompressor-3096 | https://github.com/vllm-project/llm-compressor/pull/3096 | 2026-08-28 | python | logic | 1 | added |
| case-mcpb-221 | https://github.com/modelcontextprotocol/mcpb/pull/221 | 2026-04-13 | typescript | logic | 1 | added |
| case-megatronlm-6955 | https://github.com/NVIDIA/Megatron-LM/pull/6955 | 2026-08-28 | python | logic | 3 | deletion-only, deletion-only, deletion-only |
| case-megatronlm-6982 | https://github.com/NVIDIA/Megatron-LM/pull/6982 | 2026-09-02 | python | logic | 1 | added |
| case-modeloptimizer-2332 | https://github.com/NVIDIA/Model-Optimizer/pull/2332 | 2026-09-04 | python | logic | 3 | deletion-only, deletion-only, deletion-only |
| case-nvidiacontainertoolkit-2025 | https://github.com/NVIDIA/nvidia-container-toolkit/pull/2025 | 2026-08-25 | go | logic | 1 | added |
| case-nvidiacontainertoolkit-2042 | https://github.com/NVIDIA/nvidia-container-toolkit/pull/2042 | 2026-09-02 | go | logic | 2 | added, added |
| case-olmocookbook-178 | https://github.com/allenai/olmo-cookbook/pull/178 | 2025-11-05 | python | security | 3 | added, added, deletion-only |
| case-olmocore-596 | https://github.com/allenai/OLMo-core/pull/596 | 2026-02-05 | python | logic | 1 | added |
| case-olmocore-600 | https://github.com/allenai/OLMo-core/pull/600 | 2026-02-08 | python | logic | 1 | deletion-only |
| case-olmocore-601 | https://github.com/allenai/OLMo-core/pull/601 | 2026-02-10 | python | logic | 3 | added, added, added |
| case-olmocore-614 | https://github.com/allenai/OLMo-core/pull/614 | 2026-02-20 | python | logic | 1 | added |
| case-olmocore-645 | https://github.com/allenai/OLMo-core/pull/645 | 2026-03-25 | python | logic | 1 | added |
| case-olmocore-670 | https://github.com/allenai/OLMo-core/pull/670 | 2026-05-06 | python | logic | 1 | added |
| case-openaiagentsjs-1767 | https://github.com/openai/openai-agents-js/pull/1767 | 2026-08-28 | typescript | security | 1 | deletion-only |
| case-openaiagentsjs-1769 | https://github.com/openai/openai-agents-js/pull/1769 | 2026-08-28 | typescript | logic | 2 | added, added |
| case-openaiagentsjs-1822 | https://github.com/openai/openai-agents-js/pull/1822 | 2026-09-05 | typescript | logic | 1 | deletion-only |
| case-openaiagentspython-4663 | https://github.com/openai/openai-agents-python/pull/4663 | 2026-08-26 | python | security | 2 | added, added |
| case-openaiagentspython-4676 | https://github.com/openai/openai-agents-python/pull/4676 | 2026-08-27 | python | security | 1 | added |
| case-openaiagentspython-4692 | https://github.com/openai/openai-agents-python/pull/4692 | 2026-08-27 | python | security | 1 | deletion-only |
| case-openaiagentspython-4707 | https://github.com/openai/openai-agents-python/pull/4707 | 2026-08-27 | python | security | 2 | added, added |
| case-openaidotnet-1193 | https://github.com/openai/openai-dotnet/pull/1193 | 2026-06-16 | csharp | logic | 1 | added |
| case-openaidotnet-1228 | https://github.com/openai/openai-dotnet/pull/1228 | 2026-07-24 | csharp | logic | 1 | added |
| case-openaidotnet-1230 | https://github.com/openai/openai-dotnet/pull/1230 | 2026-07-22 | csharp | logic | 1 | added |
| case-openaidotnet-1317 | https://github.com/openai/openai-dotnet/pull/1317 | 2026-08-24 | csharp | logic | 3 | added, added, deletion-only |
| case-openaijava-875 | https://github.com/openai/openai-java/pull/875 | 2026-08-18 | kotlin | logic | 1 | deletion-only |
| case-openainode-2628 | https://github.com/openai/openai-node/pull/2628 | 2026-09-05 | typescript | security | 1 | added |
| case-openainode-2642 | https://github.com/openai/openai-node/pull/2642 | 2026-09-05 | typescript | logic | 2 | added, deletion-only |
| case-openaipython-3757 | https://github.com/openai/openai-python/pull/3757 | 2026-08-28 | python | logic | 2 | deletion-only, added |
| case-openaipython-3799 | https://github.com/openai/openai-python/pull/3799 | 2026-09-04 | python | logic | 2 | added, deletion-only |
| case-openairuby-655 | https://github.com/openai/openai-ruby/pull/655 | 2026-09-06 | ruby | security | 1 | added |
| case-openairuby-656 | https://github.com/openai/openai-ruby/pull/656 | 2026-09-06 | ruby | security | 2 | added, added |
| case-openairuby-660 | https://github.com/openai/openai-ruby/pull/660 | 2026-09-06 | ruby | logic | 2 | deletion-only, added |
| case-openairuby-662 | https://github.com/openai/openai-ruby/pull/662 | 2026-09-06 | ruby | logic | 1 | added |
| case-openinstruct-1605 | https://github.com/allenai/open-instruct/pull/1605 | 2026-04-14 | python | logic | 1 | deletion-only |
| case-openinstruct-1612 | https://github.com/allenai/open-instruct/pull/1612 | 2026-04-17 | python | logic | 1 | added |
| case-openinstruct-1674 | https://github.com/allenai/open-instruct/pull/1674 | 2026-05-12 | python | logic | 2 | added, deletion-only |
| case-openinstruct-1685 | https://github.com/allenai/open-instruct/pull/1685 | 2026-05-12 | python | logic | 1 | added |
| case-openinstruct-1686 | https://github.com/allenai/open-instruct/pull/1686 | 2026-05-12 | python | logic | 2 | added, added |
| case-openinstruct-1716 | https://github.com/allenai/open-instruct/pull/1716 | 2026-06-10 | python | logic | 2 | added, added |
| case-openinstruct-1809 | https://github.com/allenai/open-instruct/pull/1809 | 2026-08-11 | python | logic | 2 | deletion-only, added |
| case-pkl-1816 | https://github.com/apple/pkl/pull/1816 | 2026-08-25 | java | logic | 1 | added |
| case-pklgo-228 | https://github.com/apple/pkl-go/pull/228 | 2026-06-26 | go | logic | 1 | added |
| case-pklgo-232 | https://github.com/apple/pkl-go/pull/232 | 2026-04-21 | go | security | 1 | deletion-only |
| case-pklgo-256 | https://github.com/apple/pkl-go/pull/256 | 2026-07-13 | go | logic | 3 | added, deletion-only, deletion-only |
| case-productionstack-1017 | https://github.com/vllm-project/production-stack/pull/1017 | 2026-08-05 | python | logic | 3 | added, deletion-only, deletion-only |
| case-productionstack-1021 | https://github.com/vllm-project/production-stack/pull/1021 | 2026-07-28 | python | logic | 1 | added |
| case-pythonsdk-3086 | https://github.com/modelcontextprotocol/python-sdk/pull/3086 | 2026-07-17 | python | logic | 2 | added, added |
| case-raft-3125 | https://github.com/NVIDIA/raft/pull/3125 | 2026-08-26 | cuda | logic | 1 | deletion-only |
| case-raft-3134 | https://github.com/NVIDIA/raft/pull/3134 | 2026-09-03 | cpp | logic | 1 | added |
| case-rl-3989 | https://github.com/NVIDIA-NeMo/RL/pull/3989 | 2026-09-04 | python | logic | 1 | deletion-only |
| case-rslearn-605 | https://github.com/allenai/rslearn/pull/605 | 2026-04-13 | python | logic | 3 | added, added, added |
| case-rslearn-646 | https://github.com/allenai/rslearn/pull/646 | 2026-05-11 | python | logic | 1 | added |
| case-rslearn-648 | https://github.com/allenai/rslearn/pull/648 | 2026-05-21 | python | logic | 1 | added |
| case-rslearn-697 | https://github.com/allenai/rslearn/pull/697 | 2026-08-11 | python | logic | 1 | added |
| case-rslearn-698 | https://github.com/allenai/rslearn/pull/698 | 2026-08-04 | python | logic | 1 | added |
| case-semanticrouter-3504 | https://github.com/vllm-project/semantic-router/pull/3504 | 2026-09-05 | go | logic | 1 | added |
| case-servers-4717 | https://github.com/modelcontextprotocol/servers/pull/4717 | 2026-09-03 | typescript | logic | 3 | added, added, added |
| case-servicetalk-3581 | https://github.com/apple/servicetalk/pull/3581 | 2026-07-22 | java | logic | 3 | added, added, added |
| case-servicetalk-3604 | https://github.com/apple/servicetalk/pull/3604 | 2026-08-12 | java | logic | 1 | deletion-only |
| case-sourcekitlsp-2722 | https://github.com/swiftlang/sourcekit-lsp/pull/2722 | 2026-07-16 | swift | logic | 2 | added, added |
| case-speech-16146 | https://github.com/NVIDIA-NeMo/Speech/pull/16146 | 2026-08-26 | python | logic | 2 | deletion-only, deletion-only |
| case-speech-16169 | https://github.com/NVIDIA-NeMo/Speech/pull/16169 | 2026-09-04 | python | logic | 1 | added |
| case-speech-16173 | https://github.com/NVIDIA-NeMo/Speech/pull/16173 | 2026-09-02 | python | logic | 1 | added |
| case-swift-91927 | https://github.com/swiftlang/swift/pull/91927 | 2026-09-04 | cpp | logic | 2 | added, deletion-only |
| case-swift-91965 | https://github.com/swiftlang/swift/pull/91965 | 2026-09-04 | cpp | logic | 1 | added |
| case-swiftargumentparser-838 | https://github.com/apple/swift-argument-parser/pull/838 | 2025-12-18 | swift | logic | 3 | deletion-only, deletion-only, added |
| case-swiftargumentparser-866 | https://github.com/apple/swift-argument-parser/pull/866 | 2026-03-20 | swift | logic | 1 | added |
| case-swiftargumentparser-873 | https://github.com/apple/swift-argument-parser/pull/873 | 2026-03-19 | swift | logic | 1 | added |
| case-swiftasyncalgorithms-387 | https://github.com/apple/swift-async-algorithms/pull/387 | 2026-01-26 | swift | logic | 1 | added |
| case-swiftbuild-1650 | https://github.com/swiftlang/swift-build/pull/1650 | 2026-08-18 | swift | logic | 2 | deletion-only, deletion-only |
| case-swiftcertificates-307 | https://github.com/apple/swift-certificates/pull/307 | 2026-08-27 | swift | logic | 2 | added, added |
| case-swiftcollections-659 | https://github.com/apple/swift-collections/pull/659 | 2026-05-27 | swift | logic | 3 | added, added, added |
| case-swiftcollections-679 | https://github.com/apple/swift-collections/pull/679 | 2026-07-07 | swift | logic | 2 | deletion-only, added |
| case-swiftcollections-697 | https://github.com/apple/swift-collections/pull/697 | 2026-08-11 | swift | logic | 3 | added, added, added |
| case-swiftcollections-718 | https://github.com/apple/swift-collections/pull/718 | 2026-09-04 | swift | logic | 1 | deletion-only |
| case-swiftconfiguration-151 | https://github.com/apple/swift-configuration/pull/151 | 2026-01-30 | swift | logic | 2 | added, added |
| case-swiftcorelibsfoundation-5502 | https://github.com/swiftlang/swift-corelibs-foundation/pull/5502 | 2026-07-07 | c | logic | 1 | added |
| case-swiftcrypto-423 | https://github.com/apple/swift-crypto/pull/423 | 2025-10-29 | swift | logic | 3 | added, deletion-only, added |
| case-swiftdriver-2097 | https://github.com/swiftlang/swift-driver/pull/2097 | 2026-03-05 | swift | logic | 2 | deletion-only, deletion-only |
| case-swiftdriver-2114 | https://github.com/swiftlang/swift-driver/pull/2114 | 2026-04-09 | swift | logic | 1 | added |
| case-swiftformat-1227 | https://github.com/swiftlang/swift-format/pull/1227 | 2026-06-26 | swift | logic | 1 | deletion-only |
| case-swiftfoundation-2196 | https://github.com/swiftlang/swift-foundation/pull/2196 | 2026-08-31 | swift | logic | 1 | added |
| case-swiftlog-411 | https://github.com/apple/swift-log/pull/411 | 2026-02-16 | swift | logic | 2 | added, added |
| case-swiftnioextras-304 | https://github.com/apple/swift-nio-extras/pull/304 | 2026-01-28 | swift | logic | 2 | added, added |
| case-swiftnioextras-319 | https://github.com/apple/swift-nio-extras/pull/319 | 2026-07-20 | swift | logic | 1 | deletion-only |
| case-swiftopenapigenerator-898 | https://github.com/apple/swift-openapi-generator/pull/898 | 2026-04-24 | swift | logic | 1 | added |
| case-swiftopenapigenerator-939 | https://github.com/apple/swift-openapi-generator/pull/939 | 2026-08-20 | swift | logic | 3 | added, deletion-only, deletion-only |
| case-swiftsyntax-3326 | https://github.com/swiftlang/swift-syntax/pull/3326 | 2026-05-08 | swift | logic | 3 | added, deletion-only, deletion-only |
| case-tensorrt-4653 | https://github.com/NVIDIA/TensorRT/pull/4653 | 2025-12-11 | python | logic | 3 | added, added, deletion-only |
| case-tensorrt-4836 | https://github.com/NVIDIA/TensorRT/pull/4836 | 2026-08-25 | python | logic | 1 | added |
| case-tensorrtllm-18694 | https://github.com/NVIDIA/TensorRT-LLM/pull/18694 | 2026-09-04 | cuda | logic | 1 | added |
| case-tpuinference-3492 | https://github.com/vllm-project/tpu-inference/pull/3492 | 2026-09-04 | python | logic | 3 | deletion-only, deletion-only, deletion-only |
| case-tpuinference-3505 | https://github.com/vllm-project/tpu-inference/pull/3505 | 2026-09-03 | python | logic | 2 | added, added |
| case-transformerengine-3440 | https://github.com/NVIDIA/TransformerEngine/pull/3440 | 2026-09-01 | cuda | logic | 1 | deletion-only |
| case-triton-11546 | https://github.com/triton-lang/triton/pull/11546 | 2026-09-02 | cpp | logic | 1 | added |
| case-triton-11558 | https://github.com/triton-lang/triton/pull/11558 | 2026-09-02 | cpp | logic | 1 | added |
| case-vllm-55455 | https://github.com/vllm-project/vllm/pull/55455 | 2026-09-06 | python | logic | 1 | deletion-only |
| case-vllm-55461 | https://github.com/vllm-project/vllm/pull/55461 | 2026-09-06 | python | logic | 2 | deletion-only, added |
| case-vllmascend-15784 | https://github.com/vllm-project/vllm-ascend/pull/15784 | 2026-09-04 | python | logic | 1 | deletion-only |
| case-vllmascend-15819 | https://github.com/vllm-project/vllm-ascend/pull/15819 | 2026-09-06 | python | logic | 1 | deletion-only |
| case-vllmascend-15840 | https://github.com/vllm-project/vllm-ascend/pull/15840 | 2026-09-05 | python | logic | 1 | deletion-only |
| case-vllmgaudi-1773 | https://github.com/vllm-project/vllm-gaudi/pull/1773 | 2026-08-31 | python | logic | 2 | deletion-only, added |
| case-vllmgaudi-1780 | https://github.com/vllm-project/vllm-gaudi/pull/1780 | 2026-09-03 | python | logic | 3 | deletion-only, deletion-only, deletion-only |
| case-vllmgaudi-1782 | https://github.com/vllm-project/vllm-gaudi/pull/1782 | 2026-09-05 | python | logic | 2 | deletion-only, deletion-only |
| case-vllmomni-7162 | https://github.com/vllm-project/vllm-omni/pull/7162 | 2026-09-06 | python | logic | 1 | deletion-only |
| case-warp-1879 | https://github.com/NVIDIA/warp/pull/1879 | 2026-09-02 | python | logic | 1 | added |
| case-whisper-2812 | https://github.com/openai/whisper/pull/2812 | 2026-07-28 | python | logic | 1 | deletion-only |

183 cases, 314 seeded bugs.

## Licensing of the excerpts

Each case embeds a short excerpt (the reversed hunks of one merged pull request) from the repository linked in its row. Those excerpts remain under their original licenses and their copyright stays with their authors; the link is the attribution. The repository's own license covers the engine, the tooling and the labels, not the excerpts.
