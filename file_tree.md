L9/
   agent/
   agents/
   api/                        # Active API endpoints (legacy moved to archive)
   archive/                    # Archived/obsolete code (cleanup completed)
       api_legacy/             # Legacy API files: memory_api, memory_client, server_memory, tasks_debug, twilio_client, webhook_whatsapp
       l_prod/                 # Shadow OS v0 (L v0) - production runtime files
       l_runtime/              # Shadow OS v0 (L v0) - runtime files
       l_staging/              # Shadow OS v0 (L v0) - staging files
       mac_v0/                 # Mac Agent v0: agent.py, exec_agent.py
       safety_prod/            # Old governance/safety modules - production
       safety_runtime/         # Old governance/safety modules - runtime
       safety_staging/         # Old governance/safety modules - staging
   checkpoints/
   clients/
   collaborative_cells/
   config/
   core/
   data/
   deploy/
   docs/
   DOCS-IB/
   ir_engine/
   langgraph/
   mac_agent/                  # Active Mac Agent (config, install scripts, plists)
   memory/                     # Active memory system
       client/
       extractor/
           ingestion/inbox
           outbox/
   migrations/
   orchestration/
   orchestrators/
   os/
   production/                 # Active production runtime (l/ and modules/safety/ moved to archive)
       governance/             # Active governance system
       l/                      # Empty (moved to archive/l_prod)
       l9_runtime/
       memory_kg/
       modules/
           safety/             # Empty (moved to archive/safety_prod)
       ops/
       tests/
       tools/
   prompts/
   qdrant/
   runtime/                    # Active runtime (l/ and modules/safety/ moved to archive)
       governance/             # Active governance system
       l/                      # Empty (moved to archive/l_runtime)
       l9_runtime/
       memory_kg/
       modules/
           safety/             # Empty (moved to archive/safety_runtime)
       ops/
       tests/
       tools/
   seed/
   services/
   simulation/
   staging/                    # Active staging (l/ and modules/safety/ moved to archive)
       governance/             # Active governance system
       l/                      # Empty (moved to archive/l_staging)
       l9_runtime/
       memory_kg/
       modules/
           safety/             # Empty (moved to archive/safety_staging)
       ops/
       tests/
       tools/
   storage/
   telemetry/
   tests/
   tools/
   world_model/
