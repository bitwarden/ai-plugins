#!/bin/bash
# run-init-chain.sh - Chain Anthropic's /init with Bitwarden enhancement
# Usage: ./run-init-chain.sh [working-directory]
#
# This script runs two phases:
# 1. Anthropic's default /init to generate initial CLAUDE.md
# 2. Bitwarden's enhancement command to extend with our template

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKING_DIR="${1:-${PWD}}"
CLAUDE_MD_PATH="${WORKING_DIR}/CLAUDE.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Check if claude CLI is available
if ! command -v claude &> /dev/null; then
    log_error "claude CLI is not installed or not in PATH"
    log_error "Install Claude Code: https://claude.ai/code"
    exit 1
fi

# Change to working directory
cd "${WORKING_DIR}"
log_info "Working directory: ${WORKING_DIR}"

# Check if CLAUDE.md already exists
if [ -f "${CLAUDE_MD_PATH}" ]; then
    log_warning "CLAUDE.md already exists at ${CLAUDE_MD_PATH}"
    log_info "Phase 1 will update the existing file"
fi

echo ""
echo "=========================================="
echo "  Phase 1: Running Anthropic's /init"
echo "=========================================="
echo ""

log_info "Starting Claude Code with /init command..."
log_info "This will analyze your codebase and generate initial CLAUDE.md"
echo ""

# Run Phase 1: Anthropic's default /init
# Using --max-turns to prevent runaway and --dangerously-skip-permissions for non-interactive
if ! claude -p "/init" --max-turns 50 --dangerously-skip-permissions; then
    log_error "Phase 1 failed: Anthropic /init command did not complete successfully"
    exit 1
fi

# Verify CLAUDE.md was created
if [ ! -f "${CLAUDE_MD_PATH}" ]; then
    log_error "Phase 1 completed but CLAUDE.md was not created at ${CLAUDE_MD_PATH}"
    exit 1
fi

log_success "Phase 1 complete: CLAUDE.md generated"
echo ""

echo "=========================================="
echo "  Phase 2: Bitwarden Enhancement"
echo "=========================================="
echo ""

log_info "Enhancing CLAUDE.md with Bitwarden's extended template..."
log_info "This will add additional sections and do supplementary research"
echo ""

# Run Phase 2: Bitwarden enhancement
# The enhance command will read the existing CLAUDE.md and extend it
if ! claude -p "/bitwarden-init:enhance" --max-turns 75 --dangerously-skip-permissions; then
    log_error "Phase 2 failed: Bitwarden enhancement did not complete successfully"
    log_warning "The initial CLAUDE.md from Phase 1 is still available"
    exit 1
fi

log_success "Phase 2 complete: CLAUDE.md enhanced with Bitwarden template"
echo ""

echo "=========================================="
echo "  Initialization Complete"
echo "=========================================="
echo ""
log_success "CLAUDE.md has been created and enhanced at: ${CLAUDE_MD_PATH}"
log_info "Review the generated file and customize as needed"
log_info "Remember to commit CLAUDE.md to your repository"
echo ""
