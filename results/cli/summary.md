# OYSTER results across model configurations

| config | cheap-model | strong-model | path | $ total | strict | loose | seeded | $/bug (strict) | false pos | p50 latency | parse fails |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku45-sonnet5 | claude-haiku-4-5 | claude-sonnet-5 | A | $0.5132 | 13 | 14 | 21 | $0.0395 | 4 | 45.8s | 0 |
| haiku45-sonnet5 | claude-haiku-4-5 | claude-sonnet-5 | B | $0.6411 | 18 | 18 | 21 | $0.0356 | 2 | 53.3s | 0 |
| haiku45-sonnet5 | claude-haiku-4-5 | claude-sonnet-5 | C | $0.3247 | 18 | 18 | 21 | $0.0180 | 2 | 14.9s | 0 |
| haiku45-sonnet5-cheapnone | claude-haiku-4-5 | claude-sonnet-5 | A | $0.0254 | 18 | 20 | 21 | $0.0014 | 3 | 2.8s | 0 |
| haiku45-sonnet5-cheapnone | claude-haiku-4-5 | claude-sonnet-5 | B | $0.1411 | 18 | 18 | 21 | $0.0078 | 3 | 7.2s | 0 |
| haiku45-sonnet5-cheapnone | claude-haiku-4-5 | claude-sonnet-5 | C | $0.3020 | 20 | 20 | 21 | $0.0151 | 2 | 16.7s | 0 |

## Selection under the default budget

- **haiku45-sonnet5**: Selected path C: predicted quality 0.57, predicted cost $0.0244 / 59.77s rejected A: latency rejected B: latency
- **haiku45-sonnet5-cheapnone**: Selected path C: predicted quality 0.62, predicted cost $0.0224 / 95.06s
