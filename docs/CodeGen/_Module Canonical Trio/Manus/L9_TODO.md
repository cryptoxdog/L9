# L9 TODO – High-Priority System Tasks

## A. Runtime / Infra
- [ ] Install WebSocket orchestrator and /ws/agent endpoint
- [ ] Install event-stream schema and wire to orchestrator
- [ ] Centralize Pydantic schemas into core/schemas spine
- [ ] Load private kernels dynamically from /l9_private

## B. Security
- [ ] Add capability sandboxing per agent
- [ ] Implement signed WebSocket handshake (agent identity + capabilities)
- [ ] Add kernel hashing + tamper detection on startup
- [ ] Enforce PRIVATE_BOUNDARY rules in orchestrator + memory
- [ ] Define agent capability tokens / permissions model
- [ ] Harden Mac Agent (allowed tools, no raw exec)

## C. Testing
- [ ] Add end-to-end integration tests (prompt → response)
- [ ] Add tests for WebSocket orchestration
- [ ] Add tests for security kernel + capability enforcement

## D. Housekeeping
- [ ] Regenerate canonical file_tree.md
