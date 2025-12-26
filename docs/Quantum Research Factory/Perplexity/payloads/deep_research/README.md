# Sonar Deep Research Payloads

## First 5 Modules (Phase 1: Spec Generation)

| # | Module | Tier | Payload File |
|---|--------|------|--------------|
| 1 | `config_loader` | 0 | `01_config_loader.md` |
| 2 | `structlog_setup` | 0 | `02_structlog_setup.md` |
| 3 | `packet_protocol` | 2 | `03_packet_protocol.md` |
| 4 | `slack_webhook_adapter` | 4 | `04_slack_webhook_adapter.md` |
| 5 | `health_routes` | 5 | `05_health_routes.md` |

## API Details

- **Model:** `sonar-deep-research`
- **Endpoint:** `POST https://api.perplexity.ai/chat/completions`
- **Rate Limit:** 5 requests/minute (wait 12s between calls)
- **Response Time:** 2-5 minutes per query
- **Cost:** $0.50-$2.00 per query

## Usage

### Option A: Perplexity Labs UI
1. Go to https://labs.perplexity.ai/
2. Select "sonar-deep-research" model
3. Copy-paste the full payload
4. Wait for response (2-5 min)
5. Save YAML output to `generated/specs/module_name.yaml`

### Option B: API Call
```bash
curl -X POST https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

## Output

Save each spec to:
```
generated/specs/
├── config_loader.yaml
├── structlog_setup.yaml
├── packet_protocol.yaml
├── slack_webhook_adapter.yaml
└── health_routes.yaml
```

## Next Step (Phase 2)

After specs are reviewed:
- Use `Module-Prompt-PERPLEXITY-v3.0.md` to generate code from each spec

