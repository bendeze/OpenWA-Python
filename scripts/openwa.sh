#!/bin/bash
# OpenWA Smart Orchestration Script
# Reads .env and activates appropriate Docker profiles

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Log functions
log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

# Load environment variables
load_env() {
    if [ -f "$PROJECT_DIR/.env" ]; then
        log_info "Loading .env file..."
        set -a
        source "$PROJECT_DIR/.env"
        set +a
    else
        log_warn ".env file not found, using defaults"
    fi
}

# Determine which profiles to activate
get_profiles() {
    local profiles=""

    # Dashboard (default: enabled)
    if [ "${DASHBOARD_ENABLED:-true}" = "true" ]; then
        profiles="$profiles --profile with-dashboard"
        log_info "Dashboard: enabled"
    fi

    # Proxy (default: enabled)
    if [ "${PROXY_ENABLED:-true}" = "true" ]; then
        profiles="$profiles --profile with-proxy"
        log_info "Proxy (Traefik): enabled"
    fi

    # PostgreSQL (built-in)
    if [ "${DATABASE_TYPE:-sqlite}" = "postgres" ] && [ "${POSTGRES_BUILTIN:-false}" = "true" ]; then
        profiles="$profiles --profile postgres"
        log_info "PostgreSQL: built-in container"
    elif [ "${DATABASE_TYPE:-sqlite}" = "postgres" ]; then
        log_info "PostgreSQL: external (${DATABASE_HOST:-localhost}:${DATABASE_PORT:-5432})"
    else
        log_info "Database: SQLite"
    fi

    # Redis (built-in)
    if [ "${REDIS_ENABLED:-false}" = "true" ] && [ "${REDIS_BUILTIN:-false}" = "true" ]; then
        profiles="$profiles --profile redis"
        log_info "Redis: built-in container"
    elif [ "${REDIS_ENABLED:-false}" = "true" ]; then
        log_info "Redis: external (${REDIS_HOST:-localhost}:${REDIS_PORT:-6379})"
    else
        log_info "Redis: disabled"
    fi

    # MinIO (built-in S3)
    if [ "${STORAGE_TYPE:-local}" = "s3" ] && [ "${MINIO_BUILTIN:-false}" = "true" ]; then
        profiles="$profiles --profile minio"
        log_info "Storage: built-in MinIO"
    elif [ "${STORAGE_TYPE:-local}" = "s3" ]; then
        log_info "Storage: external S3 (${S3_ENDPOINT})"
    else
        log_info "Storage: local filesystem"
    fi

    # Engine type
    log_info "Engine: ${ENGINE_TYPE:-whatsapp-web.js}"

    echo "$profiles"
}

# Validate engine type
validate_engine() {
    local engine="${ENGINE_TYPE:-whatsapp-web.js}"
    local valid_engines=("whatsapp-web.js" "baileys")

    for valid in "${valid_engines[@]}"; do
        if [ "$engine" = "$valid" ]; then
            return 0
        fi
    done

    log_error "Invalid ENGINE_TYPE: $engine"
    log_error "Valid options: ${valid_engines[*]}"
    exit 1
}

# Start OpenWA
cmd_start() {
    log_info "Starting OpenWA..."
    load_env
    validate_engine

    local profiles=$(get_profiles)

    echo ""
    log_info "Activating profiles:$profiles"
    echo ""

    cd "$PROJECT_DIR"
    docker compose $profiles up -d

    echo ""
    log_success "OpenWA started successfully!"
    echo ""
    log_info "Dashboard: http://localhost:${DASHBOARD_PORT:-2886}"
    log_info "API: http://localhost:${API_PORT:-2785}"
}

# Stop OpenWA
cmd_stop() {
    log_info "Stopping OpenWA..."
    cd "$PROJECT_DIR"
    docker compose --profile postgres --profile redis --profile minio --profile with-dashboard --profile with-proxy down
    log_success "OpenWA stopped"
}

# Restart OpenWA
cmd_restart() {
    cmd_stop
    cmd_start
}

# Show status
cmd_status() {
    log_info "OpenWA container status:"
    echo ""
    cd "$PROJECT_DIR"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
}

# Show logs
cmd_logs() {
    local service="${1:-openwa-api}"
    local lines="${2:-100}"
    cd "$PROJECT_DIR"
    docker compose logs -f --tail="$lines" "$service"
}

# Build images
cmd_build() {
    log_info "Building OpenWA images..."
    load_env
    local profiles=$(get_profiles)
    cd "$PROJECT_DIR"
    docker compose $profiles build
    log_success "Build complete"
}

# Update (pull + build + restart)
cmd_update() {
    log_info "Updating OpenWA..."
    cd "$PROJECT_DIR"
    git pull
    cmd_build
    cmd_restart
    log_success "Update complete"
}

# Show help
cmd_help() {
    echo ""
    echo "OpenWA Smart Orchestration Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start       Start OpenWA with auto-detected profiles"
    echo "  stop        Stop all OpenWA containers"
    echo "  restart     Restart OpenWA"
    echo "  status      Show container status"
    echo "  logs        Show logs (default: openwa-api)"
    echo "  build       Build Docker images"
    echo "  update      Pull latest code and restart"
    echo "  help        Show this help"
    echo ""
    echo "Profile activation is automatic based on .env:"
    echo "  POSTGRES_BUILTIN=true  → activates postgres profile"
    echo "  REDIS_BUILTIN=true     → activates redis profile"
    echo "  MINIO_BUILTIN=true     → activates minio profile"
    echo ""
}

# Main
case "${1:-help}" in
    start)   cmd_start ;;
    stop)    cmd_stop ;;
    restart) cmd_restart ;;
    status)  cmd_status ;;
    logs)    cmd_logs "${2:-}" "${3:-}" ;;
    build)   cmd_build ;;
    update)  cmd_update ;;
    help)    cmd_help ;;
    *)
        log_error "Unknown command: $1"
        cmd_help
        exit 1
        ;;
esac
