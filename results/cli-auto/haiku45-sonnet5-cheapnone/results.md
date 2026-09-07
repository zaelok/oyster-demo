# OYSTER results

Generated: 2026-09-07T02:06:39Z
Corpus: 183 cases, 314 seeded bugs, corpus commit 6ce6f4c4fafc5f3894692b983e20dc0faf7c962f
Models: cheap-model=claude-haiku-4-5 @ $1.00/$5.00 per 1M
        strong-model=claude-sonnet-5 @ $2.00/$10.00 per 1M
Provider: claude-code: claude-haiku-4-5 effort=none, claude-sonnet-5 effort=default; API-reported tokens

| path | description | $ total | strict caught | loose caught | seeded | $/bug (strict) | p50 latency | halted |
|------|-------------|---------|---------------|--------------|--------|----------------|-------------|--------|
| A | single cheap pass: cheap-scanner(cheap-model) | $0.3129 | 192 | 235 | 314 | $0.0016 | 2.83s | 0 |
| B | cascade: cheap-scanner(cheap-model) -> deep-reviewer(strong-model) | $2.6304 | 184 | 223 | 314 | $0.0143 | 9.04s | 0 |
| C | bounded iteration: deep-reviewer -> critic -> deep-reviewer (strong-model) | $5.4959 | 177 | 206 | 314 | $0.0311 | 19.81s | 0 |

## Per-case detail

### Path A

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-anthropicsdkcsharp-236 | $0.0012 | 2.39s | case-anthropicsdkcsharp-236-b1 | case-anthropicsdkcsharp-236-b1 | - | 0 | - |
| case-anthropicsdkjava-295 | $0.0015 | 2.32s | case-anthropicsdkjava-295-b1 | case-anthropicsdkjava-295-b1 | - | 0 | - |
| case-anthropicsdkjava-309 | $0.0014 | 2.67s | case-anthropicsdkjava-309-b1 | case-anthropicsdkjava-309-b1 | case-anthropicsdkjava-309-b2 | 0 | - |
| case-anthropicsdkjava-382 | $0.0024 | 3.70s | case-anthropicsdkjava-382-b1, case-anthropicsdkjava-382-b2 | case-anthropicsdkjava-382-b1, case-anthropicsdkjava-382-b2 | - | 0 | - |
| case-anthropicsdkpython-1124 | $0.0018 | 3.50s | case-anthropicsdkpython-1124-b1 | case-anthropicsdkpython-1124-b1 | - | 1 | - |
| case-anthropicsdkpython-1244 | $0.0014 | 2.54s | case-anthropicsdkpython-1244-b1 | case-anthropicsdkpython-1244-b1 | case-anthropicsdkpython-1244-b2 | 0 | - |
| case-anthropicsdkpython-1275 | $0.0011 | 2.70s | case-anthropicsdkpython-1275-b1 | case-anthropicsdkpython-1275-b1 | - | 0 | - |
| case-anthropicsdkpython-1642 | $0.0013 | 2.63s | case-anthropicsdkpython-1642-b1 | case-anthropicsdkpython-1642-b1 | case-anthropicsdkpython-1642-b2 | 0 | - |
| case-anthropicsdkruby-124 | $0.0010 | 2.54s | case-anthropicsdkruby-124-b1 | case-anthropicsdkruby-124-b1 | - | 0 | - |
| case-anthropicsdkruby-126 | $0.0019 | 2.84s | case-anthropicsdkruby-126-b2 | case-anthropicsdkruby-126-b1, case-anthropicsdkruby-126-b2 | - | 0 | - |
| case-anthropicsdkruby-189 | $0.0012 | 2.64s | case-anthropicsdkruby-189-b1 | case-anthropicsdkruby-189-b1 | - | 0 | - |
| case-anthropicsdktypescript-1021 | $0.0014 | 2.71s | case-anthropicsdktypescript-1021-b1 | case-anthropicsdktypescript-1021-b1 | case-anthropicsdktypescript-1021-b2, case-anthropicsdktypescript-1021-b3 | 0 | - |
| case-anthropicsdktypescript-856 | $0.0018 | 1.95s | case-anthropicsdktypescript-856-b1, case-anthropicsdktypescript-856-b2 | case-anthropicsdktypescript-856-b1, case-anthropicsdktypescript-856-b2 | - | 0 | - |
| case-apex-2018 | $0.0042 | 5.29s | case-apex-2018-b1, case-apex-2018-b3 | case-apex-2018-b1, case-apex-2018-b2, case-apex-2018-b3 | - | 0 | - |
| case-beakergantry-185 | $0.0017 | 3.32s | case-beakergantry-185-b1, case-beakergantry-185-b2 | case-beakergantry-185-b1, case-beakergantry-185-b2 | - | 0 | - |
| case-cccl-11103 | $0.0013 | 2.58s | case-cccl-11103-b1 | case-cccl-11103-b1 | - | 0 | - |
| case-cccl-11176 | $0.0020 | 3.67s | case-cccl-11176-b1 | case-cccl-11176-b1 | - | 0 | - |
| case-claudeagentsdkpython-1058 | $0.0024 | 4.21s | case-claudeagentsdkpython-1058-b1, case-claudeagentsdkpython-1058-b2 | case-claudeagentsdkpython-1058-b1, case-claudeagentsdkpython-1058-b2 | case-claudeagentsdkpython-1058-b3 | 1 | - |
| case-claudecodeaction-1692 | $0.0012 | 2.40s | - | case-claudecodeaction-1692-b1 | - | 0 | - |
| case-codex-4944 | $0.0022 | 3.64s | case-codex-4944-b1 | case-codex-4944-b1, case-codex-4944-b3 | case-codex-4944-b2 | 0 | - |
| case-codex-4967 | $0.0023 | 4.32s | case-codex-4967-b1, case-codex-4967-b2 | case-codex-4967-b1, case-codex-4967-b2 | - | 0 | - |
| case-codex-4992 | $0.0013 | 2.61s | case-codex-4992-b1 | case-codex-4992-b1 | - | 0 | - |
| case-codex-5016 | $0.0024 | 4.14s | case-codex-5016-b1 | case-codex-5016-b1, case-codex-5016-b2 | - | 0 | - |
| case-codex-5069 | $0.0022 | 3.38s | case-codex-5069-b1 | case-codex-5069-b1, case-codex-5069-b2 | - | 0 | - |
| case-container-2138 | $0.0012 | 2.51s | - | case-container-2138-b1 | - | 0 | - |
| case-containerization-794 | $0.0016 | 2.56s | case-containerization-794-b1 | case-containerization-794-b1 | - | 0 | - |
| case-containerization-833 | $0.0021 | 3.89s | case-containerization-833-b2 | case-containerization-833-b2 | case-containerization-833-b1, case-containerization-833-b3 | 0 | - |
| case-containerization-856 | $0.0012 | 2.47s | case-containerization-856-b1 | case-containerization-856-b1 | - | 0 | - |
| case-coremltools-2770 | $0.0013 | 2.65s | case-coremltools-2770-b1 | case-coremltools-2770-b1 | - | 0 | - |
| case-coremltools-2771 | $0.0032 | 4.73s | case-coremltools-2771-b2, case-coremltools-2771-b3 | case-coremltools-2771-b2, case-coremltools-2771-b3 | case-coremltools-2771-b1 | 0 | - |
| case-coremltools-2774 | $0.0013 | 2.51s | case-coremltools-2774-b1 | case-coremltools-2774-b1 | case-coremltools-2774-b2 | 0 | - |
| case-coremltools-2778 | $0.0014 | 2.96s | case-coremltools-2778-b1 | case-coremltools-2778-b1 | - | 0 | - |
| case-cudapython-2739 | $0.0013 | 2.73s | case-cudapython-2739-b1 | case-cudapython-2739-b1 | - | 0 | - |
| case-cudf-23973 | $0.0021 | 3.55s | case-cudf-23973-b2 | case-cudf-23973-b2, case-cudf-23973-b3 | case-cudf-23973-b1 | 0 | - |
| case-cudfspark-15870 | $0.0016 | 2.66s | case-cudfspark-15870-b2 | case-cudfspark-15870-b2 | case-cudfspark-15870-b1 | 0 | - |
| case-cudfspark-15900 | $0.0021 | 3.82s | - | case-cudfspark-15900-b1, case-cudfspark-15900-b2 | - | 0 | - |
| case-cugraph-5632 | $0.0021 | 3.48s | case-cugraph-5632-b1, case-cugraph-5632-b2 | case-cugraph-5632-b1, case-cugraph-5632-b2 | - | 0 | - |
| case-cuopt-1834 | $0.0020 | 3.46s | case-cuopt-1834-b1, case-cuopt-1834-b3 | case-cuopt-1834-b1, case-cuopt-1834-b3 | case-cuopt-1834-b2 | 0 | - |
| case-cupy-10273 | $0.0014 | 3.05s | case-cupy-10273-b1 | case-cupy-10273-b1 | - | 0 | - |
| case-cutlass-3427 | $0.0028 | 4.93s | case-cutlass-3427-b1 | case-cutlass-3427-b1 | case-cutlass-3427-b2, case-cutlass-3427-b3 | 0 | - |
| case-cutlass-3461 | $0.0021 | 3.34s | case-cutlass-3461-b1, case-cutlass-3461-b2 | case-cutlass-3461-b1, case-cutlass-3461-b2 | - | 0 | - |
| case-cutlass-3464 | $0.0014 | 2.89s | case-cutlass-3464-b1 | case-cutlass-3464-b1 | - | 0 | - |
| case-cuvs-2513 | $0.0039 | 5.04s | case-cuvs-2513-b1 | case-cuvs-2513-b1 | case-cuvs-2513-b2, case-cuvs-2513-b3 | 0 | - |
| case-dali-6422 | $0.0011 | 2.71s | case-dali-6422-b1 | case-dali-6422-b1 | - | 0 | - |
| case-dali-6458 | $0.0013 | 2.51s | case-dali-6458-b1 | case-dali-6458-b1 | - | 0 | - |
| case-flashattention-178 | $0.0019 | 3.36s | case-flashattention-178-b2 | case-flashattention-178-b1, case-flashattention-178-b2 | case-flashattention-178-b3 | 0 | - |
| case-flashattention-192 | $0.0015 | 2.63s | case-flashattention-192-b3 | case-flashattention-192-b3 | case-flashattention-192-b1, case-flashattention-192-b2 | 0 | - |
| case-flashattention-2787 | $0.0030 | 4.82s | case-flashattention-2787-b2 | case-flashattention-2787-b2 | case-flashattention-2787-b1, case-flashattention-2787-b3 | 2 | - |
| case-gosdk-1176 | $0.0013 | 2.80s | case-gosdk-1176-b1 | case-gosdk-1176-b1 | case-gosdk-1176-b2 | 0 | - |
| case-gosdk-1184 | $0.0013 | 2.54s | case-gosdk-1184-b2 | case-gosdk-1184-b2 | case-gosdk-1184-b1 | 0 | - |
| case-gosdk-1221 | $0.0013 | 2.47s | case-gosdk-1221-b1 | case-gosdk-1221-b1 | case-gosdk-1221-b2, case-gosdk-1221-b3 | 0 | - |
| case-gptoss-163 | $0.0013 | 2.51s | case-gptoss-163-b2 | case-gptoss-163-b2 | case-gptoss-163-b1 | 0 | - |
| case-gptoss-182 | $0.0012 | 2.57s | case-gptoss-182-b1 | case-gptoss-182-b1 | - | 0 | - |
| case-gptoss-194 | $0.0012 | 2.31s | case-gptoss-194-b1 | case-gptoss-194-b1 | - | 0 | - |
| case-gptoss-250 | $0.0018 | 3.31s | - | case-gptoss-250-b2 | case-gptoss-250-b1, case-gptoss-250-b3 | 0 | - |
| case-gpuoperator-2792 | $0.0029 | 4.60s | - | case-gpuoperator-2792-b1, case-gpuoperator-2792-b2, case-gpuoperator-2792-b3 | - | 0 | - |
| case-guidellm-1072 | $0.0025 | 3.63s | case-guidellm-1072-b1, case-guidellm-1072-b2 | case-guidellm-1072-b1, case-guidellm-1072-b2 | case-guidellm-1072-b3 | 0 | - |
| case-inspector-2267 | $0.0020 | 3.47s | case-inspector-2267-b2 | case-inspector-2267-b2 | case-inspector-2267-b1 | 1 | - |
| case-javasdk-1104 | $0.0015 | 2.63s | case-javasdk-1104-b1 | case-javasdk-1104-b1 | - | 0 | - |
| case-javasdk-1109 | $0.0015 | 2.73s | case-javasdk-1109-b1 | case-javasdk-1109-b1 | - | 0 | - |
| case-k8sdeviceplugin-1928 | $0.0014 | 2.63s | case-k8sdeviceplugin-1928-b2 | case-k8sdeviceplugin-1928-b2 | case-k8sdeviceplugin-1928-b1 | 0 | - |
| case-k8sdeviceplugin-1995 | $0.0022 | 3.74s | - | case-k8sdeviceplugin-1995-b1, case-k8sdeviceplugin-1995-b2, case-k8sdeviceplugin-1995-b3 | - | 0 | - |
| case-kotlinsdk-912 | $0.0017 | 2.47s | case-kotlinsdk-912-b1 | case-kotlinsdk-912-b1 | - | 0 | - |
| case-kvikio-990 | $0.0014 | 2.72s | case-kvikio-990-b1 | case-kvikio-990-b1 | - | 0 | - |
| case-litellm-39780 | $0.0024 | 3.50s | case-litellm-39780-b2 | case-litellm-39780-b2 | case-litellm-39780-b1, case-litellm-39780-b3 | 0 | - |
| case-litellm-39815 | $0.0019 | 3.17s | case-litellm-39815-b2 | case-litellm-39815-b2 | case-litellm-39815-b1 | 1 | - |
| case-litellm-39848 | $0.0019 | 3.77s | - | case-litellm-39848-b1 | - | 1 | - |
| case-litellm-39871 | $0.0013 | 2.83s | - | case-litellm-39871-b1 | - | 0 | - |
| case-litellm-39873 | $0.0021 | 3.55s | case-litellm-39873-b1, case-litellm-39873-b2 | case-litellm-39873-b1, case-litellm-39873-b2 | - | 0 | - |
| case-litellm-39955 | $0.0016 | 2.58s | - | - | case-litellm-39955-b1, case-litellm-39955-b2 | 1 | - |
| case-litellm-39960 | $0.0020 | 3.94s | - | case-litellm-39960-b1, case-litellm-39960-b2 | - | 0 | - |
| case-litellm-39964 | $0.0020 | 3.38s | case-litellm-39964-b1, case-litellm-39964-b2 | case-litellm-39964-b1, case-litellm-39964-b2 | case-litellm-39964-b3 | 0 | - |
| case-litellm-39972 | $0.0014 | 2.63s | case-litellm-39972-b1 | case-litellm-39972-b1 | - | 0 | - |
| case-llmcompressor-3070 | $0.0016 | 2.58s | case-llmcompressor-3070-b1 | case-llmcompressor-3070-b1 | - | 0 | - |
| case-llmcompressor-3079 | $0.0014 | 2.97s | case-llmcompressor-3079-b2 | case-llmcompressor-3079-b2 | case-llmcompressor-3079-b1 | 0 | - |
| case-llmcompressor-3096 | $0.0012 | 2.49s | case-llmcompressor-3096-b1 | case-llmcompressor-3096-b1 | - | 0 | - |
| case-mcpb-221 | $0.0011 | 2.63s | case-mcpb-221-b1 | case-mcpb-221-b1 | - | 0 | - |
| case-megatronlm-6955 | $0.0016 | 2.65s | case-megatronlm-6955-b3 | case-megatronlm-6955-b3 | case-megatronlm-6955-b1, case-megatronlm-6955-b2 | 0 | - |
| case-megatronlm-6982 | $0.0013 | 3.09s | case-megatronlm-6982-b1 | case-megatronlm-6982-b1 | - | 0 | - |
| case-modeloptimizer-2332 | $0.0024 | 4.06s | case-modeloptimizer-2332-b2, case-modeloptimizer-2332-b3 | case-modeloptimizer-2332-b1, case-modeloptimizer-2332-b2, case-modeloptimizer-2332-b3 | - | 0 | - |
| case-nvidiacontainertoolkit-2025 | $0.0013 | 2.19s | - | - | case-nvidiacontainertoolkit-2025-b1 | 1 | - |
| case-nvidiacontainertoolkit-2042 | $0.0021 | 3.48s | case-nvidiacontainertoolkit-2042-b1, case-nvidiacontainertoolkit-2042-b2 | case-nvidiacontainertoolkit-2042-b1, case-nvidiacontainertoolkit-2042-b2 | - | 0 | - |
| case-olmocookbook-178 | $0.0024 | 3.39s | - | case-olmocookbook-178-b1, case-olmocookbook-178-b2, case-olmocookbook-178-b3 | - | 0 | - |
| case-olmocore-596 | $0.0012 | 2.77s | case-olmocore-596-b1 | case-olmocore-596-b1 | - | 0 | - |
| case-olmocore-600 | $0.0013 | 2.69s | case-olmocore-600-b1 | case-olmocore-600-b1 | - | 0 | - |
| case-olmocore-601 | $0.0025 | 4.34s | case-olmocore-601-b1, case-olmocore-601-b2, case-olmocore-601-b3 | case-olmocore-601-b1, case-olmocore-601-b2, case-olmocore-601-b3 | - | 0 | - |
| case-olmocore-614 | $0.0013 | 2.63s | case-olmocore-614-b1 | case-olmocore-614-b1 | - | 0 | - |
| case-olmocore-645 | $0.0019 | 3.72s | case-olmocore-645-b1 | case-olmocore-645-b1 | - | 0 | - |
| case-olmocore-670 | $0.0015 | 2.72s | case-olmocore-670-b1 | case-olmocore-670-b1 | - | 0 | - |
| case-openaiagentsjs-1767 | $0.0012 | 2.57s | - | case-openaiagentsjs-1767-b1 | - | 0 | - |
| case-openaiagentsjs-1769 | $0.0019 | 3.28s | case-openaiagentsjs-1769-b1 | case-openaiagentsjs-1769-b1 | case-openaiagentsjs-1769-b2 | 1 | - |
| case-openaiagentsjs-1822 | $0.0012 | 3.23s | case-openaiagentsjs-1822-b1 | case-openaiagentsjs-1822-b1 | - | 0 | - |
| case-openaiagentspython-4663 | $0.0018 | 3.26s | case-openaiagentspython-4663-b1, case-openaiagentspython-4663-b2 | case-openaiagentspython-4663-b1, case-openaiagentspython-4663-b2 | - | 0 | - |
| case-openaiagentspython-4676 | $0.0011 | 2.19s | case-openaiagentspython-4676-b1 | case-openaiagentspython-4676-b1 | - | 0 | - |
| case-openaiagentspython-4692 | $0.0012 | 2.10s | - | case-openaiagentspython-4692-b1 | - | 0 | - |
| case-openaiagentspython-4707 | $0.0019 | 3.18s | - | case-openaiagentspython-4707-b1, case-openaiagentspython-4707-b2 | - | 0 | - |
| case-openaidotnet-1193 | $0.0012 | 2.32s | case-openaidotnet-1193-b1 | case-openaidotnet-1193-b1 | - | 0 | - |
| case-openaidotnet-1228 | $0.0012 | 2.52s | case-openaidotnet-1228-b1 | case-openaidotnet-1228-b1 | - | 0 | - |
| case-openaidotnet-1230 | $0.0014 | 2.49s | case-openaidotnet-1230-b1 | case-openaidotnet-1230-b1 | - | 0 | - |
| case-openaidotnet-1317 | $0.0020 | 4.03s | case-openaidotnet-1317-b1 | case-openaidotnet-1317-b1 | case-openaidotnet-1317-b2, case-openaidotnet-1317-b3 | 0 | - |
| case-openaijava-875 | $0.0012 | 2.51s | case-openaijava-875-b1 | case-openaijava-875-b1 | - | 0 | - |
| case-openainode-2628 | $0.0013 | 2.71s | - | case-openainode-2628-b1 | - | 0 | - |
| case-openainode-2642 | $0.0014 | 2.48s | case-openainode-2642-b1 | case-openainode-2642-b1 | case-openainode-2642-b2 | 0 | - |
| case-openaipython-3757 | $0.0018 | 3.78s | case-openaipython-3757-b1, case-openaipython-3757-b2 | case-openaipython-3757-b1, case-openaipython-3757-b2 | - | 0 | - |
| case-openaipython-3799 | $0.0020 | 3.65s | case-openaipython-3799-b1 | case-openaipython-3799-b1 | case-openaipython-3799-b2 | 0 | - |
| case-openairuby-655 | $0.0013 | 2.67s | - | case-openairuby-655-b1 | - | 0 | - |
| case-openairuby-656 | $0.0019 | 3.37s | - | case-openairuby-656-b1, case-openairuby-656-b2 | - | 0 | - |
| case-openairuby-660 | $0.0014 | 2.75s | case-openairuby-660-b2 | case-openairuby-660-b2 | case-openairuby-660-b1 | 0 | - |
| case-openairuby-662 | $0.0014 | 2.60s | - | - | case-openairuby-662-b1 | 1 | - |
| case-openinstruct-1605 | $0.0012 | 1.79s | case-openinstruct-1605-b1 | case-openinstruct-1605-b1 | - | 0 | - |
| case-openinstruct-1612 | $0.0012 | 1.54s | case-openinstruct-1612-b1 | case-openinstruct-1612-b1 | - | 0 | - |
| case-openinstruct-1674 | $0.0013 | 2.33s | case-openinstruct-1674-b1 | case-openinstruct-1674-b1 | case-openinstruct-1674-b2 | 0 | - |
| case-openinstruct-1685 | $0.0012 | 1.30s | case-openinstruct-1685-b1 | case-openinstruct-1685-b1 | - | 0 | - |
| case-openinstruct-1686 | $0.0037 | 7.88s | case-openinstruct-1686-b1, case-openinstruct-1686-b2 | case-openinstruct-1686-b1, case-openinstruct-1686-b2 | - | 1 | - |
| case-openinstruct-1716 | $0.0009 | 0.56s | - | - | case-openinstruct-1716-b1, case-openinstruct-1716-b2 | 0 | - |
| case-openinstruct-1809 | $0.0025 | 3.62s | case-openinstruct-1809-b1 | case-openinstruct-1809-b1 | case-openinstruct-1809-b2 | 1 | - |
| case-pkl-1816 | $0.0014 | 3.39s | case-pkl-1816-b1 | case-pkl-1816-b1 | - | 0 | - |
| case-pklgo-228 | $0.0013 | 2.37s | case-pklgo-228-b1 | case-pklgo-228-b1 | - | 0 | - |
| case-pklgo-232 | $0.0011 | 2.42s | - | case-pklgo-232-b1 | - | 0 | - |
| case-pklgo-256 | $0.0014 | 2.41s | - | case-pklgo-256-b2 | case-pklgo-256-b1, case-pklgo-256-b3 | 0 | - |
| case-productionstack-1017 | $0.0031 | 5.45s | case-productionstack-1017-b2 | case-productionstack-1017-b1, case-productionstack-1017-b2 | case-productionstack-1017-b3 | 1 | - |
| case-productionstack-1021 | $0.0016 | 3.35s | case-productionstack-1021-b1 | case-productionstack-1021-b1 | - | 0 | - |
| case-pythonsdk-3086 | $0.0019 | 6.63s | case-pythonsdk-3086-b1, case-pythonsdk-3086-b2 | case-pythonsdk-3086-b1, case-pythonsdk-3086-b2 | - | 0 | - |
| case-raft-3125 | $0.0013 | 2.61s | case-raft-3125-b1 | case-raft-3125-b1 | - | 0 | - |
| case-raft-3134 | $0.0018 | 3.62s | case-raft-3134-b1 | case-raft-3134-b1 | - | 0 | - |
| case-rl-3989 | $0.0011 | 2.48s | - | case-rl-3989-b1 | - | 0 | - |
| case-rslearn-605 | $0.0035 | 4.83s | case-rslearn-605-b1, case-rslearn-605-b3 | case-rslearn-605-b1, case-rslearn-605-b3 | case-rslearn-605-b2 | 0 | - |
| case-rslearn-646 | $0.0012 | 2.68s | case-rslearn-646-b1 | case-rslearn-646-b1 | - | 0 | - |
| case-rslearn-648 | $0.0011 | 8.21s | case-rslearn-648-b1 | case-rslearn-648-b1 | - | 0 | - |
| case-rslearn-697 | $0.0012 | 2.54s | case-rslearn-697-b1 | case-rslearn-697-b1 | - | 0 | - |
| case-rslearn-698 | $0.0012 | 2.44s | case-rslearn-698-b1 | case-rslearn-698-b1 | - | 0 | - |
| case-semanticrouter-3504 | $0.0018 | 3.57s | case-semanticrouter-3504-b1 | case-semanticrouter-3504-b1 | - | 0 | - |
| case-servers-4717 | $0.0026 | 4.08s | case-servers-4717-b1 | case-servers-4717-b1 | case-servers-4717-b2, case-servers-4717-b3 | 0 | - |
| case-servicetalk-3581 | $0.0023 | 3.92s | case-servicetalk-3581-b1 | case-servicetalk-3581-b1 | case-servicetalk-3581-b2, case-servicetalk-3581-b3 | 0 | - |
| case-servicetalk-3604 | $0.0028 | 3.99s | case-servicetalk-3604-b1 | case-servicetalk-3604-b1 | - | 1 | - |
| case-sourcekitlsp-2722 | $0.0012 | 2.42s | case-sourcekitlsp-2722-b1 | case-sourcekitlsp-2722-b1 | case-sourcekitlsp-2722-b2 | 0 | - |
| case-speech-16146 | $0.0020 | 3.50s | case-speech-16146-b1, case-speech-16146-b2 | case-speech-16146-b1, case-speech-16146-b2 | - | 0 | - |
| case-speech-16169 | $0.0012 | 2.96s | case-speech-16169-b1 | case-speech-16169-b1 | - | 0 | - |
| case-speech-16173 | $0.0019 | 3.83s | case-speech-16173-b1 | case-speech-16173-b1 | - | 0 | - |
| case-swift-91927 | $0.0022 | 3.86s | case-swift-91927-b1 | case-swift-91927-b1 | case-swift-91927-b2 | 0 | - |
| case-swift-91965 | $0.0013 | 2.63s | case-swift-91965-b1 | case-swift-91965-b1 | - | 0 | - |
| case-swiftargumentparser-838 | $0.0026 | 4.35s | case-swiftargumentparser-838-b2, case-swiftargumentparser-838-b3 | case-swiftargumentparser-838-b1, case-swiftargumentparser-838-b2, case-swiftargumentparser-838-b3 | - | 0 | - |
| case-swiftargumentparser-866 | $0.0014 | 2.69s | case-swiftargumentparser-866-b1 | case-swiftargumentparser-866-b1 | - | 0 | - |
| case-swiftargumentparser-873 | $0.0010 | 2.26s | case-swiftargumentparser-873-b1 | case-swiftargumentparser-873-b1 | - | 0 | - |
| case-swiftasyncalgorithms-387 | $0.0012 | 2.73s | case-swiftasyncalgorithms-387-b1 | case-swiftasyncalgorithms-387-b1 | - | 0 | - |
| case-swiftbuild-1650 | $0.0019 | 3.58s | case-swiftbuild-1650-b1, case-swiftbuild-1650-b2 | case-swiftbuild-1650-b1, case-swiftbuild-1650-b2 | - | 0 | - |
| case-swiftcertificates-307 | $0.0021 | 3.16s | case-swiftcertificates-307-b1, case-swiftcertificates-307-b2 | case-swiftcertificates-307-b1, case-swiftcertificates-307-b2 | - | 0 | - |
| case-swiftcollections-659 | $0.0023 | 3.18s | case-swiftcollections-659-b1, case-swiftcollections-659-b3 | case-swiftcollections-659-b1, case-swiftcollections-659-b3 | case-swiftcollections-659-b2 | 0 | - |
| case-swiftcollections-679 | $0.0013 | 12.26s | - | case-swiftcollections-679-b2 | case-swiftcollections-679-b1 | 0 | - |
| case-swiftcollections-697 | $0.0026 | 4.00s | case-swiftcollections-697-b1, case-swiftcollections-697-b2, case-swiftcollections-697-b3 | case-swiftcollections-697-b1, case-swiftcollections-697-b2, case-swiftcollections-697-b3 | - | 0 | - |
| case-swiftcollections-718 | $0.0012 | 2.41s | case-swiftcollections-718-b1 | case-swiftcollections-718-b1 | - | 0 | - |
| case-swiftconfiguration-151 | $0.0018 | 3.09s | - | - | case-swiftconfiguration-151-b1, case-swiftconfiguration-151-b2 | 0 | - |
| case-swiftcorelibsfoundation-5502 | $0.0018 | 3.56s | case-swiftcorelibsfoundation-5502-b1 | case-swiftcorelibsfoundation-5502-b1 | - | 0 | - |
| case-swiftcrypto-423 | $0.0028 | 4.12s | case-swiftcrypto-423-b1, case-swiftcrypto-423-b2, case-swiftcrypto-423-b3 | case-swiftcrypto-423-b1, case-swiftcrypto-423-b2, case-swiftcrypto-423-b3 | - | 0 | - |
| case-swiftdriver-2097 | $0.0019 | 3.49s | case-swiftdriver-2097-b1, case-swiftdriver-2097-b2 | case-swiftdriver-2097-b1, case-swiftdriver-2097-b2 | - | 0 | - |
| case-swiftdriver-2114 | $0.0014 | 2.67s | case-swiftdriver-2114-b1 | case-swiftdriver-2114-b1 | - | 0 | - |
| case-swiftformat-1227 | $0.0012 | 2.56s | case-swiftformat-1227-b1 | case-swiftformat-1227-b1 | - | 0 | - |
| case-swiftfoundation-2196 | $0.0014 | 2.84s | case-swiftfoundation-2196-b1 | case-swiftfoundation-2196-b1 | - | 0 | - |
| case-swiftlog-411 | $0.0009 | 0.69s | - | - | case-swiftlog-411-b1, case-swiftlog-411-b2 | 0 | - |
| case-swiftnioextras-304 | $0.0021 | 3.13s | case-swiftnioextras-304-b1, case-swiftnioextras-304-b2 | case-swiftnioextras-304-b1, case-swiftnioextras-304-b2 | - | 0 | - |
| case-swiftnioextras-319 | $0.0012 | 2.68s | case-swiftnioextras-319-b1 | case-swiftnioextras-319-b1 | - | 0 | - |
| case-swiftopenapigenerator-898 | $0.0013 | 1.48s | case-swiftopenapigenerator-898-b1 | case-swiftopenapigenerator-898-b1 | - | 0 | - |
| case-swiftopenapigenerator-939 | $0.0023 | 3.65s | case-swiftopenapigenerator-939-b1, case-swiftopenapigenerator-939-b2 | case-swiftopenapigenerator-939-b1, case-swiftopenapigenerator-939-b2 | case-swiftopenapigenerator-939-b3 | 0 | - |
| case-swiftsyntax-3326 | $0.0023 | 4.31s | case-swiftsyntax-3326-b1, case-swiftsyntax-3326-b2 | case-swiftsyntax-3326-b1, case-swiftsyntax-3326-b2, case-swiftsyntax-3326-b3 | - | 0 | - |
| case-tensorrt-4653 | $0.0024 | 3.78s | case-tensorrt-4653-b1, case-tensorrt-4653-b2 | case-tensorrt-4653-b1, case-tensorrt-4653-b2 | case-tensorrt-4653-b3 | 0 | - |
| case-tensorrt-4836 | $0.0013 | 2.61s | case-tensorrt-4836-b1 | case-tensorrt-4836-b1 | - | 0 | - |
| case-tensorrtllm-18694 | $0.0007 | 0.65s | - | - | case-tensorrtllm-18694-b1 | 0 | - |
| case-tpuinference-3492 | $0.0016 | 2.81s | case-tpuinference-3492-b3 | case-tpuinference-3492-b3 | case-tpuinference-3492-b1, case-tpuinference-3492-b2 | 0 | - |
| case-tpuinference-3505 | $0.0022 | 3.46s | case-tpuinference-3505-b1 | case-tpuinference-3505-b1 | case-tpuinference-3505-b2 | 0 | - |
| case-transformerengine-3440 | $0.0014 | 2.71s | case-transformerengine-3440-b1 | case-transformerengine-3440-b1 | - | 0 | - |
| case-triton-11546 | $0.0017 | 2.79s | case-triton-11546-b1 | case-triton-11546-b1 | - | 0 | - |
| case-triton-11558 | $0.0015 | 3.15s | case-triton-11558-b1 | case-triton-11558-b1 | - | 0 | - |
| case-vllm-55455 | $0.0013 | 2.67s | case-vllm-55455-b1 | case-vllm-55455-b1 | - | 0 | - |
| case-vllm-55461 | $0.0018 | 2.94s | case-vllm-55461-b1 | case-vllm-55461-b1 | case-vllm-55461-b2 | 0 | - |
| case-vllmascend-15784 | $0.0013 | 2.57s | case-vllmascend-15784-b1 | case-vllmascend-15784-b1 | - | 0 | - |
| case-vllmascend-15819 | $0.0013 | 2.47s | case-vllmascend-15819-b1 | case-vllmascend-15819-b1 | - | 0 | - |
| case-vllmascend-15840 | $0.0013 | 2.60s | case-vllmascend-15840-b1 | case-vllmascend-15840-b1 | - | 0 | - |
| case-vllmgaudi-1773 | $0.0030 | 4.19s | case-vllmgaudi-1773-b2 | case-vllmgaudi-1773-b2 | case-vllmgaudi-1773-b1 | 1 | - |
| case-vllmgaudi-1780 | $0.0022 | 3.83s | case-vllmgaudi-1780-b1, case-vllmgaudi-1780-b3 | case-vllmgaudi-1780-b1, case-vllmgaudi-1780-b3 | case-vllmgaudi-1780-b2 | 0 | - |
| case-vllmgaudi-1782 | $0.0019 | 6.40s | - | case-vllmgaudi-1782-b1, case-vllmgaudi-1782-b2 | - | 0 | - |
| case-vllmomni-7162 | $0.0013 | 2.22s | case-vllmomni-7162-b1 | case-vllmomni-7162-b1 | - | 0 | - |
| case-warp-1879 | $0.0018 | 3.70s | case-warp-1879-b1 | case-warp-1879-b1 | - | 0 | - |
| case-whisper-2812 | $0.0013 | 3.03s | case-whisper-2812-b1 | case-whisper-2812-b1 | - | 0 | - |

### Path B

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-anthropicsdkcsharp-236 | $0.0050 | 5.94s | case-anthropicsdkcsharp-236-b1 | case-anthropicsdkcsharp-236-b1 | - | 0 | - |
| case-anthropicsdkjava-295 | $0.0066 | 6.57s | case-anthropicsdkjava-295-b1 | case-anthropicsdkjava-295-b1 | - | 0 | - |
| case-anthropicsdkjava-309 | $0.0060 | 7.35s | case-anthropicsdkjava-309-b1 | case-anthropicsdkjava-309-b1 | case-anthropicsdkjava-309-b2 | 0 | - |
| case-anthropicsdkjava-382 | $0.0121 | 12.25s | case-anthropicsdkjava-382-b1, case-anthropicsdkjava-382-b2 | case-anthropicsdkjava-382-b1, case-anthropicsdkjava-382-b2 | - | 0 | - |
| case-anthropicsdkpython-1124 | $0.0176 | 18.14s | case-anthropicsdkpython-1124-b1 | case-anthropicsdkpython-1124-b1 | - | 1 | - |
| case-anthropicsdkpython-1244 | $0.0063 | 7.20s | case-anthropicsdkpython-1244-b1 | case-anthropicsdkpython-1244-b1 | case-anthropicsdkpython-1244-b2 | 0 | - |
| case-anthropicsdkpython-1275 | $0.0050 | 6.96s | case-anthropicsdkpython-1275-b1 | case-anthropicsdkpython-1275-b1 | - | 0 | - |
| case-anthropicsdkpython-1642 | $0.0069 | 7.97s | case-anthropicsdkpython-1642-b1 | case-anthropicsdkpython-1642-b1 | case-anthropicsdkpython-1642-b2 | 0 | - |
| case-anthropicsdkruby-124 | $0.0028 | 4.67s | - | - | case-anthropicsdkruby-124-b1 | 0 | - |
| case-anthropicsdkruby-126 | $0.0539 | 53.84s | case-anthropicsdkruby-126-b2 | case-anthropicsdkruby-126-b2 | case-anthropicsdkruby-126-b1 | 1 | - |
| case-anthropicsdkruby-189 | $0.0051 | 6.03s | case-anthropicsdkruby-189-b1 | case-anthropicsdkruby-189-b1 | - | 0 | - |
| case-anthropicsdktypescript-1021 | $0.0057 | 6.66s | case-anthropicsdktypescript-1021-b1 | case-anthropicsdktypescript-1021-b1 | case-anthropicsdktypescript-1021-b2, case-anthropicsdktypescript-1021-b3 | 0 | - |
| case-anthropicsdktypescript-856 | $0.0083 | 7.68s | case-anthropicsdktypescript-856-b1, case-anthropicsdktypescript-856-b2 | case-anthropicsdktypescript-856-b1, case-anthropicsdktypescript-856-b2 | - | 0 | - |
| case-apex-2018 | $0.0731 | 78.71s | case-apex-2018-b1, case-apex-2018-b3 | case-apex-2018-b1, case-apex-2018-b2, case-apex-2018-b3 | - | 0 | - |
| case-beakergantry-185 | $0.0082 | 10.20s | case-beakergantry-185-b1 | case-beakergantry-185-b1 | case-beakergantry-185-b2 | 1 | - |
| case-cccl-11103 | $0.0097 | 10.25s | - | case-cccl-11103-b1 | - | 0 | - |
| case-cccl-11176 | $0.0351 | 31.52s | case-cccl-11176-b1 | case-cccl-11176-b1 | - | 1 | - |
| case-claudeagentsdkpython-1058 | $0.0105 | 10.74s | case-claudeagentsdkpython-1058-b1, case-claudeagentsdkpython-1058-b2 | case-claudeagentsdkpython-1058-b1, case-claudeagentsdkpython-1058-b2 | case-claudeagentsdkpython-1058-b3 | 0 | - |
| case-claudecodeaction-1692 | $0.0073 | 7.73s | case-claudecodeaction-1692-b1 | case-claudecodeaction-1692-b1 | - | 0 | - |
| case-codex-4944 | $0.0089 | 9.44s | case-codex-4944-b1 | case-codex-4944-b1, case-codex-4944-b3 | case-codex-4944-b2 | 0 | - |
| case-codex-4967 | $0.0216 | 21.99s | case-codex-4967-b1 | case-codex-4967-b1 | case-codex-4967-b2 | 0 | - |
| case-codex-4992 | $0.0053 | 7.55s | case-codex-4992-b1 | case-codex-4992-b1 | - | 0 | - |
| case-codex-5016 | $0.0365 | 36.22s | case-codex-5016-b1 | case-codex-5016-b1, case-codex-5016-b2 | - | 0 | - |
| case-codex-5069 | $0.0088 | 9.85s | case-codex-5069-b1 | case-codex-5069-b1, case-codex-5069-b2 | - | 0 | - |
| case-container-2138 | $0.0047 | 8.73s | - | case-container-2138-b1 | - | 0 | - |
| case-containerization-794 | $0.0074 | 8.48s | case-containerization-794-b1 | case-containerization-794-b1 | - | 0 | - |
| case-containerization-833 | $0.0116 | 11.77s | case-containerization-833-b2 | case-containerization-833-b2 | case-containerization-833-b1, case-containerization-833-b3 | 0 | - |
| case-containerization-856 | $0.0032 | 4.81s | - | - | case-containerization-856-b1 | 0 | - |
| case-coremltools-2770 | $0.0055 | 6.64s | case-coremltools-2770-b1 | case-coremltools-2770-b1 | - | 0 | - |
| case-coremltools-2771 | $0.0638 | 63.13s | case-coremltools-2771-b2, case-coremltools-2771-b3 | case-coremltools-2771-b2, case-coremltools-2771-b3 | case-coremltools-2771-b1 | 0 | - |
| case-coremltools-2774 | $0.0076 | 9.18s | case-coremltools-2774-b1 | case-coremltools-2774-b1 | case-coremltools-2774-b2 | 0 | - |
| case-coremltools-2778 | $0.0437 | 46.02s | case-coremltools-2778-b1 | case-coremltools-2778-b1 | - | 0 | - |
| case-cudapython-2739 | $0.0063 | 7.07s | case-cudapython-2739-b1 | case-cudapython-2739-b1 | - | 0 | - |
| case-cudf-23973 | $0.0565 | 52.57s | - | - | case-cudf-23973-b1, case-cudf-23973-b2, case-cudf-23973-b3 | 0 | - |
| case-cudfspark-15870 | $0.0066 | 6.85s | case-cudfspark-15870-b2 | case-cudfspark-15870-b2 | case-cudfspark-15870-b1 | 0 | - |
| case-cudfspark-15900 | $0.0169 | 17.82s | - | case-cudfspark-15900-b2 | case-cudfspark-15900-b1 | 0 | - |
| case-cugraph-5632 | $0.0082 | 11.12s | case-cugraph-5632-b1, case-cugraph-5632-b2 | case-cugraph-5632-b1, case-cugraph-5632-b2 | - | 0 | - |
| case-cuopt-1834 | $0.0198 | 23.65s | case-cuopt-1834-b1, case-cuopt-1834-b3 | case-cuopt-1834-b1, case-cuopt-1834-b3 | case-cuopt-1834-b2 | 0 | - |
| case-cupy-10273 | $0.0069 | 8.72s | case-cupy-10273-b1 | case-cupy-10273-b1 | - | 0 | - |
| case-cutlass-3427 | $0.0558 | 54.65s | case-cutlass-3427-b1, case-cutlass-3427-b3 | case-cutlass-3427-b1, case-cutlass-3427-b3 | case-cutlass-3427-b2 | 0 | - |
| case-cutlass-3461 | $0.0094 | 12.56s | case-cutlass-3461-b1, case-cutlass-3461-b2 | case-cutlass-3461-b1, case-cutlass-3461-b2 | - | 0 | - |
| case-cutlass-3464 | $0.0055 | 6.87s | case-cutlass-3464-b1 | case-cutlass-3464-b1 | - | 0 | - |
| case-cuvs-2513 | $0.0711 | 70.26s | case-cuvs-2513-b1 | case-cuvs-2513-b1 | case-cuvs-2513-b2, case-cuvs-2513-b3 | 0 | - |
| case-dali-6422 | $0.0051 | 7.25s | case-dali-6422-b1 | case-dali-6422-b1 | - | 0 | - |
| case-dali-6458 | $0.0053 | 6.21s | case-dali-6458-b1 | case-dali-6458-b1 | - | 0 | - |
| case-flashattention-178 | $0.0157 | 15.05s | case-flashattention-178-b1, case-flashattention-178-b2 | case-flashattention-178-b1, case-flashattention-178-b2 | case-flashattention-178-b3 | 0 | - |
| case-flashattention-192 | $0.0126 | 16.06s | case-flashattention-192-b1 | case-flashattention-192-b1 | case-flashattention-192-b2, case-flashattention-192-b3 | 0 | - |
| case-flashattention-2787 | $0.0115 | 13.50s | case-flashattention-2787-b2 | case-flashattention-2787-b2 | case-flashattention-2787-b1, case-flashattention-2787-b3 | 1 | - |
| case-gosdk-1176 | $0.0052 | 5.70s | case-gosdk-1176-b1 | case-gosdk-1176-b1 | case-gosdk-1176-b2 | 0 | - |
| case-gosdk-1184 | $0.0053 | 8.46s | case-gosdk-1184-b2 | case-gosdk-1184-b2 | case-gosdk-1184-b1 | 0 | - |
| case-gosdk-1221 | $0.0060 | 6.57s | case-gosdk-1221-b1 | case-gosdk-1221-b1 | case-gosdk-1221-b2, case-gosdk-1221-b3 | 0 | - |
| case-gptoss-163 | $0.0942 | 97.72s | case-gptoss-163-b2 | case-gptoss-163-b2 | case-gptoss-163-b1 | 0 | - |
| case-gptoss-182 | $0.0046 | 5.73s | case-gptoss-182-b1 | case-gptoss-182-b1 | - | 0 | - |
| case-gptoss-194 | $0.0045 | 7.41s | case-gptoss-194-b1 | case-gptoss-194-b1 | - | 0 | - |
| case-gptoss-250 | $0.0071 | 7.99s | - | case-gptoss-250-b2, case-gptoss-250-b3 | case-gptoss-250-b1 | 0 | - |
| case-gpuoperator-2792 | $0.0387 | 35.40s | - | case-gpuoperator-2792-b1, case-gpuoperator-2792-b2, case-gpuoperator-2792-b3 | - | 0 | - |
| case-guidellm-1072 | $0.0486 | 42.59s | case-guidellm-1072-b1, case-guidellm-1072-b2 | case-guidellm-1072-b1, case-guidellm-1072-b2 | case-guidellm-1072-b3 | 0 | - |
| case-inspector-2267 | $0.0410 | 41.92s | case-inspector-2267-b2 | case-inspector-2267-b2 | case-inspector-2267-b1 | 1 | - |
| case-javasdk-1104 | $0.0064 | 6.93s | case-javasdk-1104-b1 | case-javasdk-1104-b1 | - | 0 | - |
| case-javasdk-1109 | $0.0067 | 8.50s | case-javasdk-1109-b1 | case-javasdk-1109-b1 | - | 0 | - |
| case-k8sdeviceplugin-1928 | $0.0071 | 7.57s | case-k8sdeviceplugin-1928-b1, case-k8sdeviceplugin-1928-b2 | case-k8sdeviceplugin-1928-b1, case-k8sdeviceplugin-1928-b2 | - | 0 | - |
| case-k8sdeviceplugin-1995 | $0.0079 | 8.23s | - | case-k8sdeviceplugin-1995-b1, case-k8sdeviceplugin-1995-b2, case-k8sdeviceplugin-1995-b3 | - | 0 | - |
| case-kotlinsdk-912 | $0.0137 | 13.59s | case-kotlinsdk-912-b1 | case-kotlinsdk-912-b1 | - | 0 | - |
| case-kvikio-990 | $0.0051 | 5.69s | case-kvikio-990-b1 | case-kvikio-990-b1 | - | 0 | - |
| case-litellm-39780 | $0.0141 | 12.23s | case-litellm-39780-b2 | case-litellm-39780-b2 | case-litellm-39780-b1, case-litellm-39780-b3 | 0 | - |
| case-litellm-39815 | $0.0154 | 16.19s | case-litellm-39815-b2 | case-litellm-39815-b2 | case-litellm-39815-b1 | 1 | - |
| case-litellm-39848 | $0.0078 | 9.20s | - | case-litellm-39848-b1 | - | 1 | - |
| case-litellm-39871 | $0.0053 | 7.53s | - | case-litellm-39871-b1 | - | 0 | - |
| case-litellm-39873 | $0.0090 | 10.01s | case-litellm-39873-b1, case-litellm-39873-b2 | case-litellm-39873-b1, case-litellm-39873-b2 | - | 0 | - |
| case-litellm-39955 | $0.0090 | 9.68s | case-litellm-39955-b2 | case-litellm-39955-b2 | case-litellm-39955-b1 | 0 | - |
| case-litellm-39960 | $0.0083 | 9.79s | - | case-litellm-39960-b1, case-litellm-39960-b2 | - | 0 | - |
| case-litellm-39964 | $0.0078 | 8.77s | case-litellm-39964-b1, case-litellm-39964-b3 | case-litellm-39964-b1, case-litellm-39964-b3 | case-litellm-39964-b2 | 0 | - |
| case-litellm-39972 | $0.0070 | 8.15s | - | case-litellm-39972-b1 | - | 0 | - |
| case-llmcompressor-3070 | $0.0064 | 6.24s | case-llmcompressor-3070-b1 | case-llmcompressor-3070-b1 | - | 0 | - |
| case-llmcompressor-3079 | $0.0060 | 7.58s | case-llmcompressor-3079-b2 | case-llmcompressor-3079-b2 | case-llmcompressor-3079-b1 | 0 | - |
| case-llmcompressor-3096 | $0.0186 | 19.94s | case-llmcompressor-3096-b1 | case-llmcompressor-3096-b1 | - | 0 | - |
| case-mcpb-221 | $0.0044 | 5.73s | case-mcpb-221-b1 | case-mcpb-221-b1 | - | 0 | - |
| case-megatronlm-6955 | $0.0069 | 7.77s | case-megatronlm-6955-b1 | case-megatronlm-6955-b1 | case-megatronlm-6955-b2, case-megatronlm-6955-b3 | 0 | - |
| case-megatronlm-6982 | $0.0107 | 13.04s | case-megatronlm-6982-b1 | case-megatronlm-6982-b1 | - | 0 | - |
| case-modeloptimizer-2332 | $0.0105 | 10.79s | - | case-modeloptimizer-2332-b1 | case-modeloptimizer-2332-b2, case-modeloptimizer-2332-b3 | 2 | - |
| case-nvidiacontainertoolkit-2025 | $0.0054 | 6.30s | case-nvidiacontainertoolkit-2025-b1 | case-nvidiacontainertoolkit-2025-b1 | - | 0 | - |
| case-nvidiacontainertoolkit-2042 | $0.0162 | 16.42s | case-nvidiacontainertoolkit-2042-b1 | case-nvidiacontainertoolkit-2042-b1 | case-nvidiacontainertoolkit-2042-b2 | 0 | - |
| case-olmocookbook-178 | $0.0103 | 9.43s | - | case-olmocookbook-178-b1, case-olmocookbook-178-b2, case-olmocookbook-178-b3 | - | 0 | - |
| case-olmocore-596 | $0.0047 | 6.61s | case-olmocore-596-b1 | case-olmocore-596-b1 | - | 0 | - |
| case-olmocore-600 | $0.0053 | 6.80s | case-olmocore-600-b1 | case-olmocore-600-b1 | - | 0 | - |
| case-olmocore-601 | $0.0578 | 59.44s | case-olmocore-601-b2, case-olmocore-601-b3 | case-olmocore-601-b2, case-olmocore-601-b3 | case-olmocore-601-b1 | 0 | - |
| case-olmocore-614 | $0.0079 | 8.92s | case-olmocore-614-b1 | case-olmocore-614-b1 | - | 0 | - |
| case-olmocore-645 | $0.0083 | 12.64s | case-olmocore-645-b1 | case-olmocore-645-b1 | - | 0 | - |
| case-olmocore-670 | $0.0065 | 9.88s | case-olmocore-670-b1 | case-olmocore-670-b1 | - | 0 | - |
| case-openaiagentsjs-1767 | $0.0049 | 6.49s | - | case-openaiagentsjs-1767-b1 | - | 0 | - |
| case-openaiagentsjs-1769 | $0.0507 | 48.64s | case-openaiagentsjs-1769-b1, case-openaiagentsjs-1769-b2 | case-openaiagentsjs-1769-b1, case-openaiagentsjs-1769-b2 | - | 0 | - |
| case-openaiagentsjs-1822 | $0.0051 | 7.21s | case-openaiagentsjs-1822-b1 | case-openaiagentsjs-1822-b1 | - | 0 | - |
| case-openaiagentspython-4663 | $0.0072 | 8.48s | case-openaiagentspython-4663-b1, case-openaiagentspython-4663-b2 | case-openaiagentspython-4663-b1, case-openaiagentspython-4663-b2 | - | 0 | - |
| case-openaiagentspython-4676 | $0.0045 | 6.23s | case-openaiagentspython-4676-b1 | case-openaiagentspython-4676-b1 | - | 0 | - |
| case-openaiagentspython-4692 | $0.0046 | 5.23s | - | case-openaiagentspython-4692-b1 | - | 0 | - |
| case-openaiagentspython-4707 | $0.0113 | 12.18s | - | case-openaiagentspython-4707-b1, case-openaiagentspython-4707-b2 | - | 0 | - |
| case-openaidotnet-1193 | $0.0050 | 5.82s | case-openaidotnet-1193-b1 | case-openaidotnet-1193-b1 | - | 0 | - |
| case-openaidotnet-1228 | $0.0056 | 7.06s | case-openaidotnet-1228-b1 | case-openaidotnet-1228-b1 | - | 0 | - |
| case-openaidotnet-1230 | $0.0066 | 7.48s | case-openaidotnet-1230-b1 | case-openaidotnet-1230-b1 | - | 1 | - |
| case-openaidotnet-1317 | $0.0173 | 18.38s | case-openaidotnet-1317-b1 | case-openaidotnet-1317-b1 | case-openaidotnet-1317-b2, case-openaidotnet-1317-b3 | 1 | - |
| case-openaijava-875 | $0.0050 | 6.25s | case-openaijava-875-b1 | case-openaijava-875-b1 | - | 0 | - |
| case-openainode-2628 | $0.0061 | 6.79s | - | case-openainode-2628-b1 | - | 0 | - |
| case-openainode-2642 | $0.0064 | 6.96s | case-openainode-2642-b1 | case-openainode-2642-b1 | case-openainode-2642-b2 | 0 | - |
| case-openaipython-3757 | $0.0089 | 10.36s | - | case-openaipython-3757-b1 | case-openaipython-3757-b2 | 0 | - |
| case-openaipython-3799 | $0.0272 | 30.61s | - | - | case-openaipython-3799-b1, case-openaipython-3799-b2 | 0 | - |
| case-openairuby-655 | $0.0055 | 11.00s | - | case-openairuby-655-b1 | - | 0 | - |
| case-openairuby-656 | $0.0079 | 8.62s | - | case-openairuby-656-b1, case-openairuby-656-b2 | - | 0 | - |
| case-openairuby-660 | $0.0057 | 7.45s | case-openairuby-660-b2 | case-openairuby-660-b2 | case-openairuby-660-b1 | 0 | - |
| case-openairuby-662 | $0.0052 | 6.10s | - | - | case-openairuby-662-b1 | 1 | - |
| case-openinstruct-1605 | $0.0048 | 9.55s | case-openinstruct-1605-b1 | case-openinstruct-1605-b1 | - | 0 | - |
| case-openinstruct-1612 | $0.0048 | 4.85s | case-openinstruct-1612-b1 | case-openinstruct-1612-b1 | - | 0 | - |
| case-openinstruct-1674 | $0.0054 | 7.20s | case-openinstruct-1674-b1 | case-openinstruct-1674-b1 | case-openinstruct-1674-b2 | 0 | - |
| case-openinstruct-1685 | $0.0046 | 4.18s | case-openinstruct-1685-b1 | case-openinstruct-1685-b1 | - | 0 | - |
| case-openinstruct-1686 | $0.0241 | 22.90s | case-openinstruct-1686-b2 | case-openinstruct-1686-b2 | case-openinstruct-1686-b1 | 0 | - |
| case-openinstruct-1716 | $0.0104 | 9.04s | case-openinstruct-1716-b1 | case-openinstruct-1716-b1 | case-openinstruct-1716-b2 | 0 | - |
| case-openinstruct-1809 | $0.0099 | 10.11s | case-openinstruct-1809-b1 | case-openinstruct-1809-b1 | case-openinstruct-1809-b2 | 1 | - |
| case-pkl-1816 | $0.0058 | 7.43s | case-pkl-1816-b1 | case-pkl-1816-b1 | - | 0 | - |
| case-pklgo-228 | $0.0057 | 5.78s | case-pklgo-228-b1 | case-pklgo-228-b1 | - | 0 | - |
| case-pklgo-232 | $0.0049 | 6.65s | - | case-pklgo-232-b1 | - | 0 | - |
| case-pklgo-256 | $0.0064 | 7.88s | - | - | case-pklgo-256-b1, case-pklgo-256-b2, case-pklgo-256-b3 | 0 | - |
| case-productionstack-1017 | $0.0133 | 16.91s | case-productionstack-1017-b2, case-productionstack-1017-b3 | case-productionstack-1017-b1, case-productionstack-1017-b2, case-productionstack-1017-b3 | - | 1 | - |
| case-productionstack-1021 | $0.0072 | 7.54s | case-productionstack-1021-b1 | case-productionstack-1021-b1 | - | 0 | - |
| case-pythonsdk-3086 | $0.0152 | 19.26s | case-pythonsdk-3086-b1 | case-pythonsdk-3086-b1, case-pythonsdk-3086-b2 | - | 0 | - |
| case-raft-3125 | $0.0056 | 7.87s | case-raft-3125-b1 | case-raft-3125-b1 | - | 0 | - |
| case-raft-3134 | $0.0359 | 37.19s | case-raft-3134-b1 | case-raft-3134-b1 | - | 0 | - |
| case-rl-3989 | $0.0044 | 9.78s | case-rl-3989-b1 | case-rl-3989-b1 | - | 0 | - |
| case-rslearn-605 | $0.0230 | 23.37s | case-rslearn-605-b1, case-rslearn-605-b3 | case-rslearn-605-b1, case-rslearn-605-b3 | case-rslearn-605-b2 | 1 | - |
| case-rslearn-646 | $0.0050 | 6.42s | case-rslearn-646-b1 | case-rslearn-646-b1 | - | 0 | - |
| case-rslearn-648 | $0.0046 | 11.47s | case-rslearn-648-b1 | case-rslearn-648-b1 | - | 0 | - |
| case-rslearn-697 | $0.0051 | 5.85s | case-rslearn-697-b1 | case-rslearn-697-b1 | - | 0 | - |
| case-rslearn-698 | $0.0054 | 7.34s | case-rslearn-698-b1 | case-rslearn-698-b1 | - | 0 | - |
| case-semanticrouter-3504 | $0.0082 | 9.33s | case-semanticrouter-3504-b1 | case-semanticrouter-3504-b1 | - | 0 | - |
| case-servers-4717 | $0.0100 | 9.64s | case-servers-4717-b1, case-servers-4717-b2 | case-servers-4717-b1, case-servers-4717-b2 | case-servers-4717-b3 | 0 | - |
| case-servicetalk-3581 | $0.0093 | 10.11s | case-servicetalk-3581-b1 | case-servicetalk-3581-b1, case-servicetalk-3581-b3 | case-servicetalk-3581-b2 | 0 | - |
| case-servicetalk-3604 | $0.0105 | 10.49s | case-servicetalk-3604-b1 | case-servicetalk-3604-b1 | - | 2 | - |
| case-sourcekitlsp-2722 | $0.0057 | 6.83s | case-sourcekitlsp-2722-b1 | case-sourcekitlsp-2722-b1 | case-sourcekitlsp-2722-b2 | 0 | - |
| case-speech-16146 | $0.0078 | 8.45s | case-speech-16146-b1, case-speech-16146-b2 | case-speech-16146-b1, case-speech-16146-b2 | - | 0 | - |
| case-speech-16169 | $0.0059 | 8.40s | case-speech-16169-b1 | case-speech-16169-b1 | - | 0 | - |
| case-speech-16173 | $0.0409 | 41.20s | case-speech-16173-b1 | case-speech-16173-b1 | - | 0 | - |
| case-swift-91927 | $0.0340 | 44.79s | - | - | case-swift-91927-b1, case-swift-91927-b2 | 0 | - |
| case-swift-91965 | $0.0062 | 7.91s | case-swift-91965-b1 | case-swift-91965-b1 | - | 0 | - |
| case-swiftargumentparser-838 | $0.0359 | 36.24s | case-swiftargumentparser-838-b2, case-swiftargumentparser-838-b3 | case-swiftargumentparser-838-b2, case-swiftargumentparser-838-b3 | case-swiftargumentparser-838-b1 | 0 | - |
| case-swiftargumentparser-866 | $0.0220 | 29.03s | case-swiftargumentparser-866-b1 | case-swiftargumentparser-866-b1 | - | 0 | - |
| case-swiftargumentparser-873 | $0.0051 | 6.90s | case-swiftargumentparser-873-b1 | case-swiftargumentparser-873-b1 | - | 0 | - |
| case-swiftasyncalgorithms-387 | $0.0290 | 32.80s | case-swiftasyncalgorithms-387-b1 | case-swiftasyncalgorithms-387-b1 | - | 0 | - |
| case-swiftbuild-1650 | $0.0090 | 9.59s | case-swiftbuild-1650-b1, case-swiftbuild-1650-b2 | case-swiftbuild-1650-b1, case-swiftbuild-1650-b2 | - | 0 | - |
| case-swiftcertificates-307 | $0.0088 | 9.04s | case-swiftcertificates-307-b1, case-swiftcertificates-307-b2 | case-swiftcertificates-307-b1, case-swiftcertificates-307-b2 | - | 0 | - |
| case-swiftcollections-659 | $0.1156 | 104.62s | case-swiftcollections-659-b1, case-swiftcollections-659-b2, case-swiftcollections-659-b3 | case-swiftcollections-659-b1, case-swiftcollections-659-b2, case-swiftcollections-659-b3 | - | 0 | - |
| case-swiftcollections-679 | $0.0084 | 17.57s | case-swiftcollections-679-b1 | case-swiftcollections-679-b1, case-swiftcollections-679-b2 | - | 0 | - |
| case-swiftcollections-697 | $0.0101 | 9.40s | case-swiftcollections-697-b1, case-swiftcollections-697-b2, case-swiftcollections-697-b3 | case-swiftcollections-697-b1, case-swiftcollections-697-b2, case-swiftcollections-697-b3 | - | 0 | - |
| case-swiftcollections-718 | $0.0106 | 11.00s | case-swiftcollections-718-b1 | case-swiftcollections-718-b1 | - | 0 | - |
| case-swiftconfiguration-151 | $0.0034 | 5.19s | - | - | case-swiftconfiguration-151-b1, case-swiftconfiguration-151-b2 | 0 | - |
| case-swiftcorelibsfoundation-5502 | $0.0202 | 20.98s | case-swiftcorelibsfoundation-5502-b1 | case-swiftcorelibsfoundation-5502-b1 | - | 0 | - |
| case-swiftcrypto-423 | $0.0170 | 15.95s | case-swiftcrypto-423-b1, case-swiftcrypto-423-b3 | case-swiftcrypto-423-b1, case-swiftcrypto-423-b3 | case-swiftcrypto-423-b2 | 0 | - |
| case-swiftdriver-2097 | $0.0084 | 8.39s | case-swiftdriver-2097-b1, case-swiftdriver-2097-b2 | case-swiftdriver-2097-b1, case-swiftdriver-2097-b2 | - | 0 | - |
| case-swiftdriver-2114 | $0.0064 | 9.53s | case-swiftdriver-2114-b1 | case-swiftdriver-2114-b1 | - | 0 | - |
| case-swiftformat-1227 | $0.0062 | 6.78s | case-swiftformat-1227-b1 | case-swiftformat-1227-b1 | - | 0 | - |
| case-swiftfoundation-2196 | $0.0063 | 7.83s | case-swiftfoundation-2196-b1 | case-swiftfoundation-2196-b1 | - | 0 | - |
| case-swiftlog-411 | $0.0144 | 15.87s | - | - | case-swiftlog-411-b1, case-swiftlog-411-b2 | 0 | - |
| case-swiftnioextras-304 | $0.0090 | 7.88s | case-swiftnioextras-304-b1, case-swiftnioextras-304-b2 | case-swiftnioextras-304-b1, case-swiftnioextras-304-b2 | - | 0 | - |
| case-swiftnioextras-319 | $0.0056 | 7.27s | case-swiftnioextras-319-b1 | case-swiftnioextras-319-b1 | - | 0 | - |
| case-swiftopenapigenerator-898 | $0.0057 | 6.13s | - | - | case-swiftopenapigenerator-898-b1 | 1 | - |
| case-swiftopenapigenerator-939 | $0.0103 | 11.84s | case-swiftopenapigenerator-939-b1, case-swiftopenapigenerator-939-b2 | case-swiftopenapigenerator-939-b1, case-swiftopenapigenerator-939-b2 | case-swiftopenapigenerator-939-b3 | 0 | - |
| case-swiftsyntax-3326 | $0.0165 | 18.47s | case-swiftsyntax-3326-b1, case-swiftsyntax-3326-b2 | case-swiftsyntax-3326-b1, case-swiftsyntax-3326-b2, case-swiftsyntax-3326-b3 | - | 0 | - |
| case-tensorrt-4653 | $0.0290 | 28.54s | case-tensorrt-4653-b1, case-tensorrt-4653-b2 | case-tensorrt-4653-b1, case-tensorrt-4653-b2 | case-tensorrt-4653-b3 | 0 | - |
| case-tensorrt-4836 | $0.0063 | 7.57s | case-tensorrt-4836-b1 | case-tensorrt-4836-b1 | - | 0 | - |
| case-tensorrtllm-18694 | $0.0108 | 12.38s | case-tensorrtllm-18694-b1 | case-tensorrtllm-18694-b1 | - | 0 | - |
| case-tpuinference-3492 | $0.0071 | 7.22s | case-tpuinference-3492-b2 | case-tpuinference-3492-b2 | case-tpuinference-3492-b1, case-tpuinference-3492-b3 | 0 | - |
| case-tpuinference-3505 | $0.0091 | 9.34s | - | - | case-tpuinference-3505-b1, case-tpuinference-3505-b2 | 2 | - |
| case-transformerengine-3440 | $0.0062 | 6.83s | case-transformerengine-3440-b1 | case-transformerengine-3440-b1 | - | 0 | - |
| case-triton-11546 | $0.0446 | 45.57s | case-triton-11546-b1 | case-triton-11546-b1 | - | 0 | - |
| case-triton-11558 | $0.0439 | 45.51s | case-triton-11558-b1 | case-triton-11558-b1 | - | 1 | - |
| case-vllm-55455 | $0.0055 | 6.21s | case-vllm-55455-b1 | case-vllm-55455-b1 | - | 0 | - |
| case-vllm-55461 | $0.0074 | 8.47s | case-vllm-55461-b1 | case-vllm-55461-b1 | case-vllm-55461-b2 | 0 | - |
| case-vllmascend-15784 | $0.0059 | 7.41s | case-vllmascend-15784-b1 | case-vllmascend-15784-b1 | - | 0 | - |
| case-vllmascend-15819 | $0.0047 | 7.66s | case-vllmascend-15819-b1 | case-vllmascend-15819-b1 | - | 0 | - |
| case-vllmascend-15840 | $0.0056 | 9.26s | case-vllmascend-15840-b1 | case-vllmascend-15840-b1 | - | 0 | - |
| case-vllmgaudi-1773 | $0.0207 | 19.98s | case-vllmgaudi-1773-b2 | case-vllmgaudi-1773-b2 | case-vllmgaudi-1773-b1 | 1 | - |
| case-vllmgaudi-1780 | $0.0172 | 17.95s | - | - | case-vllmgaudi-1780-b1, case-vllmgaudi-1780-b2, case-vllmgaudi-1780-b3 | 0 | - |
| case-vllmgaudi-1782 | $0.0142 | 17.67s | - | - | case-vllmgaudi-1782-b1, case-vllmgaudi-1782-b2 | 2 | - |
| case-vllmomni-7162 | $0.0056 | 6.53s | case-vllmomni-7162-b1 | case-vllmomni-7162-b1 | - | 0 | - |
| case-warp-1879 | $0.0406 | 37.63s | case-warp-1879-b1 | case-warp-1879-b1 | - | 0 | - |
| case-whisper-2812 | $0.0122 | 14.43s | case-whisper-2812-b1 | case-whisper-2812-b1 | - | 0 | - |

### Path C

| case | $ | latency | caught (strict) | caught (loose) | missed | false positives | halted |
|------|---|---------|-----------------|----------------|--------|-----------------|--------|
| case-anthropicsdkcsharp-236 | $0.0134 | 12.24s | case-anthropicsdkcsharp-236-b1 | case-anthropicsdkcsharp-236-b1 | - | 0 | - |
| case-anthropicsdkjava-295 | $0.0177 | 15.14s | case-anthropicsdkjava-295-b1 | case-anthropicsdkjava-295-b1 | - | 0 | - |
| case-anthropicsdkjava-309 | $0.0165 | 15.77s | case-anthropicsdkjava-309-b1 | case-anthropicsdkjava-309-b1 | case-anthropicsdkjava-309-b2 | 0 | - |
| case-anthropicsdkjava-382 | $0.0320 | 33.09s | case-anthropicsdkjava-382-b1, case-anthropicsdkjava-382-b2 | case-anthropicsdkjava-382-b1, case-anthropicsdkjava-382-b2 | - | 0 | - |
| case-anthropicsdkpython-1124 | $0.0489 | 45.70s | case-anthropicsdkpython-1124-b1 | case-anthropicsdkpython-1124-b1 | - | 1 | - |
| case-anthropicsdkpython-1244 | $0.0175 | 18.56s | case-anthropicsdkpython-1244-b1 | case-anthropicsdkpython-1244-b1 | case-anthropicsdkpython-1244-b2 | 0 | - |
| case-anthropicsdkpython-1275 | $0.0142 | 15.68s | case-anthropicsdkpython-1275-b1 | case-anthropicsdkpython-1275-b1 | - | 0 | - |
| case-anthropicsdkpython-1642 | $0.0257 | 26.67s | case-anthropicsdkpython-1642-b1 | case-anthropicsdkpython-1642-b1 | case-anthropicsdkpython-1642-b2 | 0 | - |
| case-anthropicsdkruby-124 | $0.0043 | 6.62s | - | - | case-anthropicsdkruby-124-b1 | 0 | - |
| case-anthropicsdkruby-126 | $0.0455 | 44.03s | case-anthropicsdkruby-126-b2 | case-anthropicsdkruby-126-b2 | case-anthropicsdkruby-126-b1 | 0 | - |
| case-anthropicsdkruby-189 | $0.0116 | 18.09s | - | - | case-anthropicsdkruby-189-b1 | 0 | - |
| case-anthropicsdktypescript-1021 | $0.0123 | 9.23s | case-anthropicsdktypescript-1021-b1 | case-anthropicsdktypescript-1021-b1 | case-anthropicsdktypescript-1021-b2, case-anthropicsdktypescript-1021-b3 | 0 | - |
| case-anthropicsdktypescript-856 | $0.0221 | 18.60s | case-anthropicsdktypescript-856-b1, case-anthropicsdktypescript-856-b2 | case-anthropicsdktypescript-856-b1, case-anthropicsdktypescript-856-b2 | - | 0 | - |
| case-apex-2018 | $0.0629 | 59.64s | case-apex-2018-b1 | case-apex-2018-b1 | case-apex-2018-b2, case-apex-2018-b3 | 1 | - |
| case-beakergantry-185 | $0.0505 | 48.89s | case-beakergantry-185-b1, case-beakergantry-185-b2 | case-beakergantry-185-b1, case-beakergantry-185-b2 | - | 0 | - |
| case-cccl-11103 | $0.0163 | 15.58s | - | case-cccl-11103-b1 | - | 0 | - |
| case-cccl-11176 | $0.0235 | 20.63s | case-cccl-11176-b1 | case-cccl-11176-b1 | - | 0 | - |
| case-claudeagentsdkpython-1058 | $0.0354 | 30.22s | case-claudeagentsdkpython-1058-b1, case-claudeagentsdkpython-1058-b2 | case-claudeagentsdkpython-1058-b1, case-claudeagentsdkpython-1058-b2 | case-claudeagentsdkpython-1058-b3 | 0 | - |
| case-claudecodeaction-1692 | $0.0145 | 13.00s | case-claudecodeaction-1692-b1 | case-claudecodeaction-1692-b1 | - | 0 | - |
| case-codex-4944 | $0.0339 | 29.16s | case-codex-4944-b1 | case-codex-4944-b1 | case-codex-4944-b2, case-codex-4944-b3 | 0 | - |
| case-codex-4967 | $0.0275 | 24.92s | case-codex-4967-b1 | case-codex-4967-b1 | case-codex-4967-b2 | 0 | - |
| case-codex-4992 | $0.0159 | 15.04s | case-codex-4992-b1 | case-codex-4992-b1 | - | 0 | - |
| case-codex-5016 | $0.0422 | 39.83s | case-codex-5016-b1 | case-codex-5016-b1, case-codex-5016-b2 | - | 0 | - |
| case-codex-5069 | $0.0174 | 13.19s | case-codex-5069-b1 | case-codex-5069-b1 | case-codex-5069-b2 | 1 | - |
| case-container-2138 | $0.0146 | 13.96s | - | case-container-2138-b1 | - | 0 | - |
| case-containerization-794 | $0.0196 | 18.03s | case-containerization-794-b1 | case-containerization-794-b1 | - | 0 | - |
| case-containerization-833 | $0.0616 | 55.83s | case-containerization-833-b2 | case-containerization-833-b2 | case-containerization-833-b1, case-containerization-833-b3 | 0 | - |
| case-containerization-856 | $0.0153 | 19.12s | case-containerization-856-b1 | case-containerization-856-b1 | - | 0 | - |
| case-coremltools-2770 | $0.0170 | 23.37s | case-coremltools-2770-b1 | case-coremltools-2770-b1 | - | 0 | - |
| case-coremltools-2771 | $0.0883 | 79.01s | case-coremltools-2771-b2, case-coremltools-2771-b3 | case-coremltools-2771-b2, case-coremltools-2771-b3 | case-coremltools-2771-b1 | 0 | - |
| case-coremltools-2774 | $0.0153 | 14.79s | case-coremltools-2774-b1 | case-coremltools-2774-b1 | case-coremltools-2774-b2 | 0 | - |
| case-coremltools-2778 | $0.0877 | 88.40s | case-coremltools-2778-b1 | case-coremltools-2778-b1 | - | 0 | - |
| case-cudapython-2739 | $0.0171 | 14.18s | case-cudapython-2739-b1 | case-cudapython-2739-b1 | - | 0 | - |
| case-cudf-23973 | $0.1389 | 127.83s | case-cudf-23973-b2, case-cudf-23973-b3 | case-cudf-23973-b2, case-cudf-23973-b3 | case-cudf-23973-b1 | 0 | - |
| case-cudfspark-15870 | $0.0174 | 26.19s | case-cudfspark-15870-b2 | case-cudfspark-15870-b2 | case-cudfspark-15870-b1 | 0 | - |
| case-cudfspark-15900 | $0.0357 | 31.57s | - | case-cudfspark-15900-b1, case-cudfspark-15900-b2 | - | 0 | - |
| case-cugraph-5632 | $0.0210 | 15.20s | case-cugraph-5632-b1, case-cugraph-5632-b2 | case-cugraph-5632-b1, case-cugraph-5632-b2 | - | 0 | - |
| case-cuopt-1834 | $0.0202 | 18.85s | case-cuopt-1834-b1 | case-cuopt-1834-b1 | case-cuopt-1834-b2, case-cuopt-1834-b3 | 0 | - |
| case-cupy-10273 | $0.0173 | 20.64s | case-cupy-10273-b1 | case-cupy-10273-b1 | - | 0 | - |
| case-cutlass-3427 | $0.0882 | 84.73s | case-cutlass-3427-b3 | case-cutlass-3427-b3 | case-cutlass-3427-b1, case-cutlass-3427-b2 | 0 | - |
| case-cutlass-3461 | $0.0311 | 32.52s | case-cutlass-3461-b1, case-cutlass-3461-b2 | case-cutlass-3461-b1, case-cutlass-3461-b2 | - | 0 | - |
| case-cutlass-3464 | $0.0143 | 11.37s | case-cutlass-3464-b1 | case-cutlass-3464-b1 | - | 0 | - |
| case-cuvs-2513 | $0.1204 | 118.70s | case-cuvs-2513-b1 | case-cuvs-2513-b1 | case-cuvs-2513-b2, case-cuvs-2513-b3 | 0 | - |
| case-dali-6422 | $0.0137 | 14.40s | case-dali-6422-b1 | case-dali-6422-b1 | - | 0 | - |
| case-dali-6458 | $0.0164 | 14.82s | case-dali-6458-b1 | case-dali-6458-b1 | - | 0 | - |
| case-flashattention-178 | $0.0279 | 23.62s | case-flashattention-178-b1 | case-flashattention-178-b1 | case-flashattention-178-b2, case-flashattention-178-b3 | 2 | - |
| case-flashattention-192 | $0.0491 | 41.20s | case-flashattention-192-b1 | case-flashattention-192-b1 | case-flashattention-192-b2, case-flashattention-192-b3 | 0 | - |
| case-flashattention-2787 | $0.0091 | 11.37s | - | - | case-flashattention-2787-b1, case-flashattention-2787-b2, case-flashattention-2787-b3 | 0 | - |
| case-gosdk-1176 | $0.0154 | 13.31s | case-gosdk-1176-b1 | case-gosdk-1176-b1 | case-gosdk-1176-b2 | 0 | - |
| case-gosdk-1184 | $0.0179 | 16.59s | case-gosdk-1184-b2 | case-gosdk-1184-b2 | case-gosdk-1184-b1 | 0 | - |
| case-gosdk-1221 | $0.0150 | 13.22s | case-gosdk-1221-b1 | case-gosdk-1221-b1 | case-gosdk-1221-b2, case-gosdk-1221-b3 | 0 | - |
| case-gptoss-163 | $0.1267 | 128.64s | case-gptoss-163-b1 | case-gptoss-163-b1 | case-gptoss-163-b2 | 0 | - |
| case-gptoss-182 | $0.0113 | 11.37s | case-gptoss-182-b1 | case-gptoss-182-b1 | - | 0 | - |
| case-gptoss-194 | $0.0139 | 17.73s | - | - | case-gptoss-194-b1 | 0 | - |
| case-gptoss-250 | $0.0138 | 23.98s | - | case-gptoss-250-b1, case-gptoss-250-b2 | case-gptoss-250-b3 | 0 | - |
| case-gpuoperator-2792 | $0.0328 | 27.22s | - | case-gpuoperator-2792-b2, case-gpuoperator-2792-b3 | case-gpuoperator-2792-b1 | 0 | - |
| case-guidellm-1072 | $0.0961 | 87.26s | case-guidellm-1072-b1 | case-guidellm-1072-b1 | case-guidellm-1072-b2, case-guidellm-1072-b3 | 1 | - |
| case-inspector-2267 | $0.0409 | 37.38s | case-inspector-2267-b2 | case-inspector-2267-b2 | case-inspector-2267-b1 | 1 | - |
| case-javasdk-1104 | $0.0190 | 16.80s | case-javasdk-1104-b1 | case-javasdk-1104-b1 | - | 0 | - |
| case-javasdk-1109 | $0.0175 | 16.36s | case-javasdk-1109-b1 | case-javasdk-1109-b1 | - | 0 | - |
| case-k8sdeviceplugin-1928 | $0.0223 | 22.65s | - | case-k8sdeviceplugin-1928-b1 | case-k8sdeviceplugin-1928-b2 | 0 | - |
| case-k8sdeviceplugin-1995 | $0.0219 | 19.81s | case-k8sdeviceplugin-1995-b1, case-k8sdeviceplugin-1995-b2, case-k8sdeviceplugin-1995-b3 | case-k8sdeviceplugin-1995-b1, case-k8sdeviceplugin-1995-b2, case-k8sdeviceplugin-1995-b3 | - | 0 | - |
| case-kotlinsdk-912 | $0.0225 | 19.87s | case-kotlinsdk-912-b1 | case-kotlinsdk-912-b1 | - | 0 | - |
| case-kvikio-990 | $0.0179 | 16.59s | case-kvikio-990-b1 | case-kvikio-990-b1 | - | 0 | - |
| case-litellm-39780 | $0.0240 | 18.46s | case-litellm-39780-b2 | case-litellm-39780-b2 | case-litellm-39780-b1, case-litellm-39780-b3 | 0 | - |
| case-litellm-39815 | $0.0193 | 18.86s | - | - | case-litellm-39815-b1, case-litellm-39815-b2 | 2 | - |
| case-litellm-39848 | $0.0229 | 21.45s | - | case-litellm-39848-b1 | - | 0 | - |
| case-litellm-39871 | $0.0141 | 13.57s | - | case-litellm-39871-b1 | - | 0 | - |
| case-litellm-39873 | $0.0211 | 16.95s | case-litellm-39873-b1, case-litellm-39873-b2 | case-litellm-39873-b1, case-litellm-39873-b2 | - | 0 | - |
| case-litellm-39955 | $0.0171 | 13.10s | case-litellm-39955-b2 | case-litellm-39955-b2 | case-litellm-39955-b1 | 0 | - |
| case-litellm-39960 | $0.0416 | 41.34s | - | case-litellm-39960-b2 | case-litellm-39960-b1 | 0 | - |
| case-litellm-39964 | $0.0204 | 19.45s | case-litellm-39964-b1, case-litellm-39964-b3 | case-litellm-39964-b1, case-litellm-39964-b3 | case-litellm-39964-b2 | 0 | - |
| case-litellm-39972 | $0.0188 | 16.48s | - | case-litellm-39972-b1 | - | 0 | - |
| case-llmcompressor-3070 | $0.0133 | 11.39s | case-llmcompressor-3070-b1 | case-llmcompressor-3070-b1 | - | 0 | - |
| case-llmcompressor-3079 | $0.0289 | 28.10s | case-llmcompressor-3079-b1 | case-llmcompressor-3079-b1 | case-llmcompressor-3079-b2 | 0 | - |
| case-llmcompressor-3096 | $0.0223 | 20.70s | case-llmcompressor-3096-b1 | case-llmcompressor-3096-b1 | - | 0 | - |
| case-mcpb-221 | $0.0107 | 11.77s | case-mcpb-221-b1 | case-mcpb-221-b1 | - | 0 | - |
| case-megatronlm-6955 | $0.0193 | 21.03s | case-megatronlm-6955-b3 | case-megatronlm-6955-b3 | case-megatronlm-6955-b1, case-megatronlm-6955-b2 | 0 | - |
| case-megatronlm-6982 | $0.1012 | 101.84s | case-megatronlm-6982-b1 | case-megatronlm-6982-b1 | - | 0 | - |
| case-modeloptimizer-2332 | $0.0197 | 19.84s | case-modeloptimizer-2332-b2, case-modeloptimizer-2332-b3 | case-modeloptimizer-2332-b2, case-modeloptimizer-2332-b3 | case-modeloptimizer-2332-b1 | 0 | - |
| case-nvidiacontainertoolkit-2025 | $0.0158 | 14.66s | case-nvidiacontainertoolkit-2025-b1 | case-nvidiacontainertoolkit-2025-b1 | - | 0 | - |
| case-nvidiacontainertoolkit-2042 | $0.0215 | 16.16s | case-nvidiacontainertoolkit-2042-b1 | case-nvidiacontainertoolkit-2042-b1 | case-nvidiacontainertoolkit-2042-b2 | 0 | - |
| case-olmocookbook-178 | $0.0263 | 20.04s | - | case-olmocookbook-178-b1, case-olmocookbook-178-b2, case-olmocookbook-178-b3 | - | 0 | - |
| case-olmocore-596 | $0.0142 | 13.18s | case-olmocore-596-b1 | case-olmocore-596-b1 | - | 0 | - |
| case-olmocore-600 | $0.0144 | 14.36s | case-olmocore-600-b1 | case-olmocore-600-b1 | - | 0 | - |
| case-olmocore-601 | $0.0699 | 63.93s | case-olmocore-601-b2, case-olmocore-601-b3 | case-olmocore-601-b2, case-olmocore-601-b3 | case-olmocore-601-b1 | 0 | - |
| case-olmocore-614 | $0.0254 | 26.10s | case-olmocore-614-b1 | case-olmocore-614-b1 | - | 0 | - |
| case-olmocore-645 | $0.0236 | 20.66s | case-olmocore-645-b1 | case-olmocore-645-b1 | - | 0 | - |
| case-olmocore-670 | $0.0149 | 13.84s | case-olmocore-670-b1 | case-olmocore-670-b1 | - | 0 | - |
| case-openaiagentsjs-1767 | $0.0134 | 22.81s | - | case-openaiagentsjs-1767-b1 | - | 0 | - |
| case-openaiagentsjs-1769 | $0.0467 | 40.97s | case-openaiagentsjs-1769-b1 | case-openaiagentsjs-1769-b1 | case-openaiagentsjs-1769-b2 | 0 | - |
| case-openaiagentsjs-1822 | $0.0137 | 15.84s | case-openaiagentsjs-1822-b1 | case-openaiagentsjs-1822-b1 | - | 0 | - |
| case-openaiagentspython-4663 | $0.0161 | 17.12s | case-openaiagentspython-4663-b1, case-openaiagentspython-4663-b2 | case-openaiagentspython-4663-b1, case-openaiagentspython-4663-b2 | - | 0 | - |
| case-openaiagentspython-4676 | $0.0102 | 9.73s | case-openaiagentspython-4676-b1 | case-openaiagentspython-4676-b1 | - | 0 | - |
| case-openaiagentspython-4692 | $0.0138 | 16.02s | - | case-openaiagentspython-4692-b1 | - | 0 | - |
| case-openaiagentspython-4707 | $0.0213 | 18.79s | - | case-openaiagentspython-4707-b2 | case-openaiagentspython-4707-b1 | 0 | - |
| case-openaidotnet-1193 | $0.0120 | 11.34s | case-openaidotnet-1193-b1 | case-openaidotnet-1193-b1 | - | 0 | - |
| case-openaidotnet-1228 | $0.0117 | 13.72s | case-openaidotnet-1228-b1 | case-openaidotnet-1228-b1 | - | 0 | - |
| case-openaidotnet-1230 | $0.0162 | 13.97s | case-openaidotnet-1230-b1 | case-openaidotnet-1230-b1 | - | 1 | - |
| case-openaidotnet-1317 | $0.0388 | 33.00s | case-openaidotnet-1317-b1 | case-openaidotnet-1317-b1 | case-openaidotnet-1317-b2, case-openaidotnet-1317-b3 | 1 | - |
| case-openaijava-875 | $0.0174 | 16.12s | case-openaijava-875-b1 | case-openaijava-875-b1 | - | 0 | - |
| case-openainode-2628 | $0.0169 | 15.65s | - | case-openainode-2628-b1 | - | 0 | - |
| case-openainode-2642 | $0.0158 | 14.06s | case-openainode-2642-b1 | case-openainode-2642-b1 | case-openainode-2642-b2 | 0 | - |
| case-openaipython-3757 | $0.0140 | 17.95s | - | case-openaipython-3757-b1 | case-openaipython-3757-b2 | 0 | - |
| case-openaipython-3799 | $0.0976 | 84.61s | case-openaipython-3799-b1 | case-openaipython-3799-b1 | case-openaipython-3799-b2 | 0 | - |
| case-openairuby-655 | $0.0292 | 29.46s | - | case-openairuby-655-b1 | - | 0 | - |
| case-openairuby-656 | $0.0244 | 25.91s | - | - | case-openairuby-656-b1, case-openairuby-656-b2 | 0 | - |
| case-openairuby-660 | $0.0172 | 18.03s | case-openairuby-660-b2 | case-openairuby-660-b2 | case-openairuby-660-b1 | 0 | - |
| case-openairuby-662 | $0.0140 | 15.95s | - | - | case-openairuby-662-b1 | 1 | - |
| case-openinstruct-1605 | $0.0110 | 12.21s | case-openinstruct-1605-b1 | case-openinstruct-1605-b1 | - | 0 | - |
| case-openinstruct-1612 | $0.0100 | 13.44s | case-openinstruct-1612-b1 | case-openinstruct-1612-b1 | - | 0 | - |
| case-openinstruct-1674 | $0.0141 | 13.65s | case-openinstruct-1674-b1 | case-openinstruct-1674-b1 | case-openinstruct-1674-b2 | 0 | - |
| case-openinstruct-1685 | $0.0106 | 17.38s | case-openinstruct-1685-b1 | case-openinstruct-1685-b1 | - | 0 | - |
| case-openinstruct-1686 | $0.0699 | 54.12s | case-openinstruct-1686-b2 | case-openinstruct-1686-b2 | case-openinstruct-1686-b1 | 0 | - |
| case-openinstruct-1716 | $0.0276 | 23.18s | case-openinstruct-1716-b1 | case-openinstruct-1716-b1 | case-openinstruct-1716-b2 | 0 | - |
| case-openinstruct-1809 | $0.0480 | 43.66s | case-openinstruct-1809-b1 | case-openinstruct-1809-b1 | case-openinstruct-1809-b2 | 1 | - |
| case-pkl-1816 | $0.0128 | 12.23s | case-pkl-1816-b1 | case-pkl-1816-b1 | - | 0 | - |
| case-pklgo-228 | $0.0163 | 13.29s | case-pklgo-228-b1 | case-pklgo-228-b1 | - | 0 | - |
| case-pklgo-232 | $0.0139 | 15.60s | - | case-pklgo-232-b1 | - | 0 | - |
| case-pklgo-256 | $0.0330 | 31.62s | case-pklgo-256-b1 | case-pklgo-256-b1, case-pklgo-256-b2 | case-pklgo-256-b3 | 0 | - |
| case-productionstack-1017 | $0.0267 | 21.18s | case-productionstack-1017-b1, case-productionstack-1017-b2 | case-productionstack-1017-b1, case-productionstack-1017-b2, case-productionstack-1017-b3 | - | 0 | - |
| case-productionstack-1021 | $0.0194 | 16.94s | case-productionstack-1021-b1 | case-productionstack-1021-b1 | - | 0 | - |
| case-pythonsdk-3086 | $0.0392 | 39.91s | case-pythonsdk-3086-b1 | case-pythonsdk-3086-b1, case-pythonsdk-3086-b2 | - | 0 | - |
| case-raft-3125 | $0.0141 | 15.60s | case-raft-3125-b1 | case-raft-3125-b1 | - | 0 | - |
| case-raft-3134 | $0.0243 | 26.97s | case-raft-3134-b1 | case-raft-3134-b1 | - | 0 | - |
| case-rl-3989 | $0.0162 | 17.27s | case-rl-3989-b1 | case-rl-3989-b1 | - | 0 | - |
| case-rslearn-605 | $0.0819 | 79.44s | case-rslearn-605-b1, case-rslearn-605-b2 | case-rslearn-605-b1, case-rslearn-605-b2 | case-rslearn-605-b3 | 1 | - |
| case-rslearn-646 | $0.0121 | 15.30s | case-rslearn-646-b1 | case-rslearn-646-b1 | - | 0 | - |
| case-rslearn-648 | $0.0139 | 25.72s | case-rslearn-648-b1 | case-rslearn-648-b1 | - | 0 | - |
| case-rslearn-697 | $0.0128 | 19.42s | case-rslearn-697-b1 | case-rslearn-697-b1 | - | 0 | - |
| case-rslearn-698 | $0.0218 | 23.13s | case-rslearn-698-b1 | case-rslearn-698-b1 | - | 0 | - |
| case-semanticrouter-3504 | $0.0205 | 17.30s | - | case-semanticrouter-3504-b1 | - | 0 | - |
| case-servers-4717 | $0.0184 | 14.08s | case-servers-4717-b1 | case-servers-4717-b1 | case-servers-4717-b2, case-servers-4717-b3 | 0 | - |
| case-servicetalk-3581 | $0.0258 | 22.03s | case-servicetalk-3581-b1 | case-servicetalk-3581-b1, case-servicetalk-3581-b2 | case-servicetalk-3581-b3 | 0 | - |
| case-servicetalk-3604 | $0.0180 | 13.71s | case-servicetalk-3604-b1 | case-servicetalk-3604-b1 | - | 1 | - |
| case-sourcekitlsp-2722 | $0.0151 | 14.68s | - | - | case-sourcekitlsp-2722-b1, case-sourcekitlsp-2722-b2 | 1 | - |
| case-speech-16146 | $0.0207 | 18.75s | case-speech-16146-b1, case-speech-16146-b2 | case-speech-16146-b1, case-speech-16146-b2 | - | 0 | - |
| case-speech-16169 | $0.0152 | 19.64s | case-speech-16169-b1 | case-speech-16169-b1 | - | 0 | - |
| case-speech-16173 | $0.0228 | 26.74s | case-speech-16173-b1 | case-speech-16173-b1 | - | 0 | - |
| case-swift-91927 | $0.0298 | 31.71s | - | - | case-swift-91927-b1, case-swift-91927-b2 | 0 | - |
| case-swift-91965 | $0.0151 | 16.41s | case-swift-91965-b1 | case-swift-91965-b1 | - | 0 | - |
| case-swiftargumentparser-838 | $0.1092 | 103.20s | case-swiftargumentparser-838-b2, case-swiftargumentparser-838-b3 | case-swiftargumentparser-838-b2, case-swiftargumentparser-838-b3 | case-swiftargumentparser-838-b1 | 0 | - |
| case-swiftargumentparser-866 | $0.0667 | 67.63s | - | - | case-swiftargumentparser-866-b1 | 1 | - |
| case-swiftargumentparser-873 | $0.0298 | 53.03s | case-swiftargumentparser-873-b1 | case-swiftargumentparser-873-b1 | - | 0 | - |
| case-swiftasyncalgorithms-387 | $0.0196 | 18.80s | case-swiftasyncalgorithms-387-b1 | case-swiftasyncalgorithms-387-b1 | - | 0 | - |
| case-swiftbuild-1650 | $0.0193 | 19.72s | case-swiftbuild-1650-b1 | case-swiftbuild-1650-b1 | case-swiftbuild-1650-b2 | 0 | - |
| case-swiftcertificates-307 | $0.0999 | 101.71s | - | - | case-swiftcertificates-307-b1, case-swiftcertificates-307-b2 | 0 | - |
| case-swiftcollections-659 | $0.1284 | 107.35s | case-swiftcollections-659-b1, case-swiftcollections-659-b2, case-swiftcollections-659-b3 | case-swiftcollections-659-b1, case-swiftcollections-659-b2, case-swiftcollections-659-b3 | - | 0 | - |
| case-swiftcollections-679 | $0.0201 | 23.86s | case-swiftcollections-679-b1 | case-swiftcollections-679-b1 | case-swiftcollections-679-b2 | 1 | - |
| case-swiftcollections-697 | $0.0225 | 16.73s | case-swiftcollections-697-b1, case-swiftcollections-697-b2, case-swiftcollections-697-b3 | case-swiftcollections-697-b1, case-swiftcollections-697-b2, case-swiftcollections-697-b3 | - | 0 | - |
| case-swiftcollections-718 | $0.0264 | 30.62s | case-swiftcollections-718-b1 | case-swiftcollections-718-b1 | - | 0 | - |
| case-swiftconfiguration-151 | $0.0049 | 6.10s | - | - | case-swiftconfiguration-151-b1, case-swiftconfiguration-151-b2 | 0 | - |
| case-swiftcorelibsfoundation-5502 | $0.0282 | 24.95s | case-swiftcorelibsfoundation-5502-b1 | case-swiftcorelibsfoundation-5502-b1 | - | 0 | - |
| case-swiftcrypto-423 | $0.0269 | 26.70s | case-swiftcrypto-423-b1, case-swiftcrypto-423-b3 | case-swiftcrypto-423-b1, case-swiftcrypto-423-b3 | case-swiftcrypto-423-b2 | 0 | - |
| case-swiftdriver-2097 | $0.0260 | 28.25s | case-swiftdriver-2097-b1, case-swiftdriver-2097-b2 | case-swiftdriver-2097-b1, case-swiftdriver-2097-b2 | - | 0 | - |
| case-swiftdriver-2114 | $0.0183 | 16.40s | case-swiftdriver-2114-b1 | case-swiftdriver-2114-b1 | - | 0 | - |
| case-swiftformat-1227 | $0.0190 | 21.25s | case-swiftformat-1227-b1 | case-swiftformat-1227-b1 | - | 0 | - |
| case-swiftfoundation-2196 | $0.0209 | 22.02s | case-swiftfoundation-2196-b1 | case-swiftfoundation-2196-b1 | - | 0 | - |
| case-swiftlog-411 | $0.0293 | 32.41s | - | - | case-swiftlog-411-b1, case-swiftlog-411-b2 | 0 | - |
| case-swiftnioextras-304 | $0.0240 | 23.35s | case-swiftnioextras-304-b1, case-swiftnioextras-304-b2 | case-swiftnioextras-304-b1, case-swiftnioextras-304-b2 | - | 0 | - |
| case-swiftnioextras-319 | $0.0144 | 17.44s | case-swiftnioextras-319-b1 | case-swiftnioextras-319-b1 | - | 0 | - |
| case-swiftopenapigenerator-898 | $0.0170 | 20.36s | case-swiftopenapigenerator-898-b1 | case-swiftopenapigenerator-898-b1 | - | 0 | - |
| case-swiftopenapigenerator-939 | $0.0458 | 45.43s | case-swiftopenapigenerator-939-b1, case-swiftopenapigenerator-939-b2 | case-swiftopenapigenerator-939-b1, case-swiftopenapigenerator-939-b2 | case-swiftopenapigenerator-939-b3 | 0 | - |
| case-swiftsyntax-3326 | $0.0193 | 18.14s | case-swiftsyntax-3326-b2 | case-swiftsyntax-3326-b2 | case-swiftsyntax-3326-b1, case-swiftsyntax-3326-b3 | 0 | - |
| case-tensorrt-4653 | $0.0321 | 29.30s | case-tensorrt-4653-b1 | case-tensorrt-4653-b1 | case-tensorrt-4653-b2, case-tensorrt-4653-b3 | 0 | - |
| case-tensorrt-4836 | $0.0208 | 18.38s | case-tensorrt-4836-b1 | case-tensorrt-4836-b1 | - | 0 | - |
| case-tensorrtllm-18694 | $0.0194 | 20.42s | case-tensorrtllm-18694-b1 | case-tensorrtllm-18694-b1 | - | 0 | - |
| case-tpuinference-3492 | $0.0195 | 18.63s | case-tpuinference-3492-b1 | case-tpuinference-3492-b1 | case-tpuinference-3492-b2, case-tpuinference-3492-b3 | 0 | - |
| case-tpuinference-3505 | $0.0352 | 38.58s | case-tpuinference-3505-b1 | case-tpuinference-3505-b1 | case-tpuinference-3505-b2 | 0 | - |
| case-transformerengine-3440 | $0.0184 | 20.83s | - | - | case-transformerengine-3440-b1 | 1 | - |
| case-triton-11546 | $0.3001 | 320.73s | case-triton-11546-b1 | case-triton-11546-b1 | - | 0 | - |
| case-triton-11558 | $0.0199 | 26.57s | case-triton-11558-b1 | case-triton-11558-b1 | - | 0 | - |
| case-vllm-55455 | $0.0194 | 20.51s | case-vllm-55455-b1 | case-vllm-55455-b1 | - | 0 | - |
| case-vllm-55461 | $0.0246 | 28.92s | case-vllm-55461-b1 | case-vllm-55461-b1 | case-vllm-55461-b2 | 0 | - |
| case-vllmascend-15784 | $0.0140 | 14.54s | case-vllmascend-15784-b1 | case-vllmascend-15784-b1 | - | 0 | - |
| case-vllmascend-15819 | $0.0183 | 23.04s | case-vllmascend-15819-b1 | case-vllmascend-15819-b1 | - | 0 | - |
| case-vllmascend-15840 | $0.0157 | 14.81s | case-vllmascend-15840-b1 | case-vllmascend-15840-b1 | - | 0 | - |
| case-vllmgaudi-1773 | $0.0279 | 25.81s | case-vllmgaudi-1773-b2 | case-vllmgaudi-1773-b2 | case-vllmgaudi-1773-b1 | 1 | - |
| case-vllmgaudi-1780 | $0.0145 | 14.55s | - | - | case-vllmgaudi-1780-b1, case-vllmgaudi-1780-b2, case-vllmgaudi-1780-b3 | 0 | - |
| case-vllmgaudi-1782 | $0.0265 | 26.75s | case-vllmgaudi-1782-b1, case-vllmgaudi-1782-b2 | case-vllmgaudi-1782-b1, case-vllmgaudi-1782-b2 | - | 0 | - |
| case-vllmomni-7162 | $0.0177 | 19.87s | case-vllmomni-7162-b1 | case-vllmomni-7162-b1 | - | 1 | - |
| case-warp-1879 | $0.0581 | 64.30s | case-warp-1879-b1 | case-warp-1879-b1 | - | 0 | - |
| case-whisper-2812 | $0.0220 | 22.91s | case-whisper-2812-b1 | case-whisper-2812-b1 | - | 0 | - |

## Limitations

**What the numbers do and don't show**: catch-rates are corpus-specific; N is small; seeded bugs are cleaner than wild bugs. The table supports the *claim* (§0) — that selection over measured paths is possible and auditable — not a general benchmark of any model's review ability.

### Non-Goals (this slice)

- **Unbounded runtime cycles** (convergence-criterion stopping). A cyclic graph requires a termination argument — cost budget as a **variant function**, monotonically decreasing per traversal. The DAG slice guarantees finite execution structurally; the variant-function treatment for true cycles is designed (vision doc) and is v2.
- **Runtime re-planning** (switching paths mid-run on intermediate results) and **dynamic node creation** — not on the MVP critical path; both need evaluation machinery of their own.
- **Learned quality priors** (§1.4 note) and **semantic result caching** — future work, one sentence each in the README.
- **Any hosted service.** The deliverable is a reproducible repo, not a deployment.
