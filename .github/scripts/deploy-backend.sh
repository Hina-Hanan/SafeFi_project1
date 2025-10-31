#!/bin/bash
#
# Backend Deployment Helper Script
#
# This script handles the deployment of the backend to GCP VM with:
# - Ollama service verification
# - Docker container deployment with LLM support
# - Post-deployment script execution
# - Rollback on failures
#
# Usage: ./deploy-backend.sh [VM_USER] [VM_IP] [PROJECT_PATH]
#

set -euo pipefail

# Default values
VM_USER="${1:-hinahanan2003}"
VM_IP="${2:-${GCP_VM_IP:-}}"
PROJECT_PATH="${3:-/var/lib/postgresql/SafeFi_project1}"

if [ -z "$VM_IP" ]; then
  echo "❌ VM_IP is required. Usage: $0 [VM_USER] [VM_IP] [PROJECT_PATH]"
  exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
  echo -e "${GREEN}ℹ️  $1${NC}"
}

log_warn() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
  echo -e "${RED}❌ $1${NC}"
}

# Pre-deployment checks
check_prerequisites() {
  log_info "Running pre-deployment checks..."
  
  # Check disk space (at least 5GB free)
  log_info "Checking disk space..."
  DISK_FREE=$(df -BG / | tail -1 | awk '{print $4}' | sed 's/G//')
  if [ "$DISK_FREE" -lt 5 ]; then
    log_error "Insufficient disk space: ${DISK_FREE}GB free (need at least 5GB)"
    return 1
  fi
  log_info "Disk space OK: ${DISK_FREE}GB free"
  
  # Verify Ollama service is running
  log_info "Verifying Ollama service..."
  if ! ss -tlnp | grep -q ':11434'; then
    log_error "Ollama is not listening on port 11434"
    log_info "Start Ollama with: OLLAMA_HOST=0.0.0.0:11434 nohup ollama serve > /tmp/ollama.log 2>&1 &"
    return 1
  fi
  log_info "Ollama port check passed"
  
  # Verify Ollama API is accessible
  if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_error "Ollama API is not accessible"
    return 1
  fi
  log_info "Ollama API is accessible"
  
  # Verify tinyllama model is available
  OLLAMA_MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | grep -o 'tinyllama' || echo "")
  if [ -z "$OLLAMA_MODELS" ]; then
    log_warn "tinyllama model not found. LLM features may not work."
    log_info "Install with: ollama pull tinyllama"
  else
    log_info "tinyllama model is available"
  fi
  
  return 0
}

# Backup current deployment
backup_deployment() {
  log_info "Creating backup..."
  docker compose -f docker-compose.yml -f docker-compose.llm.yml ps > /tmp/docker_backup_status.txt 2>&1 || true
  docker compose -f docker-compose.yml -f docker-compose.llm.yml logs api --tail=100 > /tmp/docker_backup_logs.txt 2>&1 || true
  log_info "Backup created"
}

# Deploy containers
deploy_containers() {
  log_info "Deploying containers..."
  
  # Stop existing containers
  log_info "Stopping existing containers..."
  docker compose -f docker-compose.yml -f docker-compose.llm.yml down || true
  
  # Build API container with LLM support
  log_info "Building API container with LLM support..."
  if ! docker compose -f docker-compose.yml -f docker-compose.llm.yml build api; then
    log_error "Docker build failed"
    return 1
  fi
  
  # Start services
  log_info "Starting services..."
  if ! docker compose -f docker-compose.yml -f docker-compose.llm.yml up -d; then
    log_error "Failed to start containers"
    return 1
  fi
  
  # Wait for database
  log_info "Waiting for database to be ready..."
  sleep 10
  
  return 0
}

# Wait for API health
wait_for_api() {
  log_info "Checking API health..."
  max_attempts=20
  attempt=0
  
  while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
      log_info "API is healthy!"
      return 0
    else
      log_info "Attempt $((attempt+1))/$max_attempts: API not ready yet..."
      sleep 5
      attempt=$((attempt+1))
    fi
  done
  
  log_error "Health check failed after $max_attempts attempts"
  docker compose -f docker-compose.yml -f docker-compose.llm.yml logs api --tail=50
  return 1
}

# Verify database state
verify_database() {
  log_info "Verifying database state..."
  DB_CHECK=$(docker compose -f docker-compose.yml -f docker-compose.llm.yml exec -T api python -c "
    from app.database.connection import SessionLocal
    from app.database.models import Protocol
    db = SessionLocal()
    try:
      count = db.query(Protocol).count()
      print(f'Protocols in DB: {count}')
      if count == 0:
        exit(1)
    finally:
      db.close()
  " 2>&1)
  
  if [ $? -ne 0 ]; then
    log_error "Database verification failed"
    echo "$DB_CHECK"
    return 1
  fi
  
  echo "$DB_CHECK"
  return 0
}

# Run post-deployment script
run_post_deployment_script() {
  local script=$1
  local timeout=${2:-300}  # 5 minutes default
  
  log_info "Running $script..."
  
  # Skip initialize_vector_store.py if RAG is not enabled
  if [ "$script" = "scripts/initialize_vector_store.py" ]; then
    RAG_ENABLED=$(docker compose -f docker-compose.yml -f docker-compose.llm.yml exec -T api python -c "import os; print(os.getenv('RAG_ENABLED', 'false'))" 2>/dev/null || echo "false")
    if [ "$RAG_ENABLED" != "true" ]; then
      log_info "Skipping $script (RAG not enabled)"
      return 0
    fi
  fi
  
  if timeout "$timeout" docker compose -f docker-compose.yml -f docker-compose.llm.yml exec -T api python "$script"; then
    log_info "$script completed successfully"
    
    # Verify database after each script
    if ! verify_database; then
      log_error "Database verification failed after $script"
      return 1
    fi
    
    return 0
  else
    local exit_code=$?
    log_error "$script failed with exit code $exit_code"
    docker compose -f docker-compose.yml -f docker-compose.llm.yml logs api --tail=30
    return 1
  fi
}

# Run all post-deployment scripts
run_post_deployment_scripts() {
  log_info "Running post-deployment scripts..."
  
  local scripts=(
    "scripts/seed_real_protocols.py"
    "scripts/real_data.py"
    "scripts/auto_update_risks.py"
    "scripts/7historical_graph.py"
    "scripts/initialize_vector_store.py"
  )
  
  local script_timeout=300  # 5 minutes per script
  
  for script in "${scripts[@]}"; do
    echo ""
    if ! run_post_deployment_script "$script" "$script_timeout"; then
      log_error "Post-deployment script execution failed"
      return 1
    fi
  done
  
  log_info "All post-deployment scripts completed successfully"
  return 0
}

# Final verification
final_verification() {
  log_info "Running final verification..."
  
  # Check API health
  if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log_error "API health check failed"
    return 1
  fi
  log_info "API health check passed"
  
  # Check LLM service if enabled
  local llm_health=$(curl -s http://localhost:8000/llm/health 2>&1 || echo "{}")
  if echo "$llm_health" | grep -q '"ollama_available":true'; then
    log_info "LLM service is available"
  else
    log_warn "LLM service may not be available"
    echo "Response: $llm_health"
  fi
  
  # Check vector store if enabled
  if echo "$llm_health" | grep -q '"vector_store_initialized":true'; then
    log_info "Vector store is initialized"
  else
    log_warn "Vector store may not be initialized"
  fi
  
  # Show deployment status
  echo ""
  log_info "Deployment Status:"
  docker compose -f docker-compose.yml -f docker-compose.llm.yml ps
  
  return 0
}

# Rollback on failure
rollback() {
  log_warn "Rolling back deployment..."
  docker compose -f docker-compose.yml -f docker-compose.llm.yml down || true
  log_warn "Containers stopped. Manual intervention may be required."
}

# Main deployment function
main() {
  cd "$PROJECT_PATH" || {
    log_error "Failed to change directory to $PROJECT_PATH"
    exit 1
  }
  
  # Set error trap for rollback
  trap rollback ERR
  
  # Run checks and deployment
  if ! check_prerequisites; then
    log_error "Pre-deployment checks failed"
    exit 1
  fi
  
  backup_deployment
  
  if ! deploy_containers; then
    log_error "Container deployment failed"
    exit 1
  fi
  
  if ! wait_for_api; then
    log_error "API health check failed"
    exit 1
  fi
  
  if ! run_post_deployment_scripts; then
    log_error "Post-deployment scripts failed"
    exit 1
  fi
  
  if ! final_verification; then
    log_error "Final verification failed"
    exit 1
  fi
  
  # Clear trap on success
  trap - ERR
  
  log_info "Deployment completed successfully!"
  return 0
}

# Execute main function
main "$@"
