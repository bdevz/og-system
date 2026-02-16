#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Agent Z — OpenClaw Deployment Script
# ═══════════════════════════════════════════════════════════════
# Deploys Agent Z (Candidate Profile Manager & Data Backbone)
# into the local OpenClaw agent directory.
#
# Usage:
#   chmod +x deploy-agent-z.sh
#   ./deploy-agent-z.sh
#
# What it does:
#   1. Checks Python >=3.9 and openpyxl dependency
#   2. Copies the Z agent folder to ~/.openclaw/agents/z/
#   3. Validates all 5 scripts load without import errors
#   4. Prints deployment summary
#
# To uninstall: rm -rf ~/.openclaw/agents/z
# ═══════════════════════════════════════════════════════════════

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SRC="$SCRIPT_DIR/agents/z"
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
DEPLOY_DIR="$OPENCLAW_HOME/agents/z"
TESTS_DIR="$SCRIPT_DIR/tests"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} $1"
        ((pass++))
    else
        echo -e "  ${RED}✗${NC} $1 — $2"
        ((fail++))
    fi
}

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Agent Z — OpenClaw Deployment"
echo "═══════════════════════════════════════════════════════"
echo ""

# ── Step 1: Pre-flight checks ──
echo "Step 1: Pre-flight checks"

# Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
    echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION (>= 3.9 required)"
    ((pass++))
else
    echo -e "  ${RED}✗${NC} Python $PYTHON_VERSION found, need >= 3.9"
    ((fail++))
    echo "    Install Python 3.9+ and try again."
    exit 1
fi

# openpyxl
if python3 -c "import openpyxl" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} openpyxl installed"
    ((pass++))
else
    echo -e "  ${YELLOW}!${NC} openpyxl not found — installing..."
    pip3 install openpyxl --quiet 2>/dev/null || pip install openpyxl --quiet 2>/dev/null
    if python3 -c "import openpyxl" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} openpyxl installed after pip"
        ((pass++))
    else
        echo -e "  ${RED}✗${NC} openpyxl install failed"
        ((fail++))
    fi
fi

# Source directory exists
if [ -d "$AGENT_SRC" ]; then
    echo -e "  ${GREEN}✓${NC} Source directory found: $AGENT_SRC"
    ((pass++))
else
    echo -e "  ${RED}✗${NC} Source not found: $AGENT_SRC"
    exit 1
fi

# agent.json exists
if [ -f "$AGENT_SRC/agent.json" ]; then
    echo -e "  ${GREEN}✓${NC} agent.json present"
    ((pass++))
else
    echo -e "  ${RED}✗${NC} agent.json missing from source"
    exit 1
fi

# ── Step 2: Deploy ──
echo ""
echo "Step 2: Deploying to $DEPLOY_DIR"

# Create OpenClaw dir if needed
mkdir -p "$OPENCLAW_HOME/agents"

# Backup existing if present
if [ -d "$DEPLOY_DIR" ]; then
    BACKUP="$DEPLOY_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "  ${YELLOW}!${NC} Existing deployment found — backing up to $BACKUP"
    mv "$DEPLOY_DIR" "$BACKUP"
fi

# Copy agent
cp -r "$AGENT_SRC" "$DEPLOY_DIR"
echo -e "  ${GREEN}✓${NC} Agent files copied"
((pass++))

# Copy test data (useful for validation)
if [ -d "$TESTS_DIR" ]; then
    mkdir -p "$DEPLOY_DIR/tests"
    cp "$TESTS_DIR/sample_crm_export.csv" "$DEPLOY_DIR/tests/" 2>/dev/null || true
    cp "$TESTS_DIR/test_agent_z_production.py" "$DEPLOY_DIR/tests/" 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Test suite copied"
    ((pass++))
fi

# ── Step 3: Validate deployed scripts ──
echo ""
echo "Step 3: Validating deployed scripts"

SCORING_DIR="$DEPLOY_DIR/workspace/skills/scoring"
CSV_DIR="$DEPLOY_DIR/workspace/skills/csv-parser"
HOTLIST_DIR="$DEPLOY_DIR/workspace/skills/hotlist-publisher"

# Test each script imports cleanly
for script_info in \
    "$SCORING_DIR/priority_calculator.py:calculate_priority,calculate_batch_priorities" \
    "$SCORING_DIR/visa_urgency_calculator.py:calculate_visa_urgency,calculate_batch_visa_urgency" \
    "$SCORING_DIR/duplicate_checker.py:check_submission" \
    "$CSV_DIR/csv_parser.py:parse_crm_export" \
    "$HOTLIST_DIR/hotlist_publisher.py:generate_hotlist"
do
    script_path="${script_info%%:*}"
    functions="${script_info##*:}"
    script_name="$(basename "$script_path")"

    if [ -f "$script_path" ]; then
        # Try importing each function
        import_ok=true
        dir_path="$(dirname "$script_path")"
        module_name="${script_name%.py}"

        for func in $(echo "$functions" | tr ',' ' '); do
            python3 -c "
import sys
sys.path.insert(0, '$dir_path')
from $module_name import $func
" 2>/dev/null
            if [ $? -ne 0 ]; then
                import_ok=false
                echo -e "  ${RED}✗${NC} $module_name.$func failed to import"
                ((fail++))
            fi
        done

        if $import_ok; then
            echo -e "  ${GREEN}✓${NC} $script_name — all functions importable"
            ((pass++))
        fi
    else
        echo -e "  ${RED}✗${NC} $script_name — file not found at $script_path"
        ((fail++))
    fi
done

# Verify config files
for config in \
    "$SCORING_DIR/priority_weights.json" \
    "$DEPLOY_DIR/agent.json"
do
    config_name="$(basename "$config")"
    if python3 -c "import json; json.load(open('$config'))" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $config_name — valid JSON"
        ((pass++))
    else
        echo -e "  ${RED}✗${NC} $config_name — invalid JSON"
        ((fail++))
    fi
done

# ── Step 4: Quick smoke test ──
echo ""
echo "Step 4: Smoke test (visa urgency calculation)"

SMOKE_RESULT=$(python3 -c "
import sys, json
from datetime import datetime, timezone, timedelta
sys.path.insert(0, '$SCORING_DIR')
from visa_urgency_calculator import calculate_visa_urgency

tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y-%m-%d')
r = calculate_visa_urgency({'consultant_id': 'SMOKE-1', 'visa_status': 'H1B', 'visa_expiration_date': tomorrow})
print(json.dumps({'tier': r['urgency_tier'], 'days': r['days_remaining']}))
" 2>&1)

if echo "$SMOKE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['tier']=='CRITICAL'" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} H1B expiring tomorrow = CRITICAL (correct)"
    ((pass++))
else
    echo -e "  ${RED}✗${NC} Smoke test failed: $SMOKE_RESULT"
    ((fail++))
fi

# ── Summary ──
echo ""
echo "═══════════════════════════════════════════════════════"
if [ $fail -eq 0 ]; then
    echo -e "  ${GREEN}DEPLOYMENT SUCCESSFUL${NC} — $pass checks passed"
    echo ""
    echo "  Agent Z deployed to: $DEPLOY_DIR"
    echo "  Config:              $DEPLOY_DIR/agent.json"
    echo "  Memory:              $DEPLOY_DIR/workspace/memory/"
    echo ""
    echo "  To run the full production test suite:"
    echo "    cd $SCRIPT_DIR && python3 tests/test_agent_z_production.py"
    echo ""
    echo "  To uninstall:"
    echo "    rm -rf $DEPLOY_DIR"
else
    echo -e "  ${RED}DEPLOYMENT FAILED${NC} — $pass passed, $fail failed"
    echo "  Fix the issues above and re-run."
    exit 1
fi
echo "═══════════════════════════════════════════════════════"
echo ""
