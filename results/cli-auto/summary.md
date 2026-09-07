# OYSTER results across model configurations

| config | cheap-model | strong-model | path | $ total | strict | loose | seeded | $/bug (strict) | false pos | p50 latency | parse fails |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku45-sonnet5-cheapnone | claude-haiku-4-5 | claude-sonnet-5 | A | $0.3129 | 192 | 235 | 314 | $0.0016 | 16 | 2.8s | 0 |
| haiku45-sonnet5-cheapnone | claude-haiku-4-5 | claude-sonnet-5 | B | $2.6304 | 184 | 223 | 314 | $0.0143 | 25 | 9.0s | 0 |
| haiku45-sonnet5-cheapnone | claude-haiku-4-5 | claude-sonnet-5 | C | $5.4959 | 177 | 206 | 314 | $0.0311 | 21 | 19.8s | 0 |

## Selection under the default budget

- **haiku45-sonnet5-cheapnone**: Selected path C: predicted quality 0.44, predicted cost $0.0376 / 107.76s
