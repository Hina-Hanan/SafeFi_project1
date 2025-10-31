<!-- a16307d0-986b-4eba-b40f-26e30e8f1262 3f5aa6e6-ccef-42fd-be48-158bf11ba2da -->
# Complete CI/CD Pipeline Setup Plan

## Overview
This plan implements a production-ready CI/CD pipeline that automatically tests, builds, and deploys the backend (with LLM support) to GCP VM and the frontend to GCS. Post-deployment scripts run automatically on every deployment with proper error handling and rollback.

## Components to Update/Create

### 1. CI Workflow (`.github/workflows/ci.yml`)
   - Already tests backend and frontend
   - Builds both slim and full LLM Docker images
   - Status: **Needs minor updates** - ensure full LLM build is properly tested

### 2. CD Backend Workflow (`.github/workflows/cd-backend.yml`)
   - **Major updates needed**:
     - Always use `docker-compose.llm.yml` for LLM support
     - Add Ollama service verification step before deployment
     - Add post-deployment script execution in order:
       1. `seed_real_protocols.py` (runs on every deployment, skips if exists)
       2. `real_data.py` (initializes/updates protocol data)
       3. `auto_update_risks.py` (calculates risk scores)
       4. `7historical_graph.py` (generates historical data)
       5. `initialize_vector_store.py` (only if LLM/RAG enabled)
     - Implement rollback mechanism on script failures
     - Add comprehensive health checks after each script
     - Improve error handling and logging

### 3. CD Frontend Workflow (`.github/workflows/cd-frontend.yml`)
   - Already builds and deploys to GCS
   - Status: **May need minor updates** for better error handling

### 4. Deployment Scripts
   - Create `.github/scripts/deploy-backend.sh` helper script
   - Include rollback logic and error handling
   - Verify Ollama service availability
   - Execute post-deployment scripts in sequence with error checking

### 5. Documentation Updates
   - Update `.github/CI_CD_SETUP.md` with:
     - Post-deployment script execution details
     - Ollama service verification steps
     - Rollback procedures
     - Troubleshooting guide for common issues

## Implementation Details

### Backend Deployment Flow
1. **Pre-deployment checks**:
   - Verify Ollama service is running on VM host
   - Check VM disk space
   - Verify SSH connectivity

2. **Deployment**:
   - Copy files to VM
   - Build Docker images with LLM support (`USE_FULL_REQS=1`)
   - Stop existing containers
   - Start new containers
   - Wait for health checks

3. **Post-deployment scripts** (in order):
   ```bash
   docker compose exec -T api python scripts/seed_real_protocols.py
   docker compose exec -T api python scripts/real_data.py
   docker compose exec -T api python scripts/auto_update_risks.py
   docker compose exec -T api python scripts/7historical_graph.py
   docker compose exec -T api python scripts/initialize_vector_store.py
   ```

4. **Verification**:
   - Health endpoint check
   - Database connectivity
   - LLM service availability
   - Vector store initialization status

5. **Rollback** (on failure):
   - Stop new containers
   - Restore previous containers (if backup exists)
   - Report failure with logs

### Error Handling
- Each script execution should have timeout (5 minutes per script)
- Log all script outputs for debugging
- Verify database state after each script
- Rollback on any critical failure (scripts, health checks, LLM initialization)

### Ollama Verification
- Check if Ollama is listening on port 11434
- Verify `tinyllama` model is available
- Test connection from container to host Ollama service
- Provide clear error messages if Ollama is not available

## Files to Modify

1. `.github/workflows/cd-backend.yml` - Add Ollama check, post-deployment scripts, rollback
2. `.github/workflows/ci.yml` - Minor improvements for LLM build testing
3. `.github/scripts/deploy-backend.sh` - New helper script for deployment logic
4. `.github/CI_CD_SETUP.md` - Update documentation

## Dependencies

- GitHub S

### To-dos

- [ ] Update cd-backend.yml to always deploy with LLM support, add Ollama verification, and include post-deployment script execution with rollback mechanism
- [ ] Create .github/scripts/deploy-backend.sh helper script with Ollama check, script execution, and rollback logic
- [ ] Update ci.yml to ensure LLM build testing is comprehensive
- [ ] Review and improve cd-frontend.yml error handling if needed
- [ ] Update CI_CD_SETUP.md with post-deployment scripts, Ollama verification, and rollback procedures