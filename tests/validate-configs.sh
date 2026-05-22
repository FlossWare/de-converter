#!/bin/bash
# Configuration Validation Script
# Tests generated fvwm and jwm configurations for syntax errors

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

FVWM_CONFIG_DIR="$PROJECT_DIR/examples/fvwm"
JWM_CONFIG="$PROJECT_DIR/examples/jwm/.jwmrc"

echo "========================================="
echo "  Configuration Validation Script"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ERRORS=0

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ==================== Validate fvwm Configuration ====================
echo "Validating fvwm configuration..."
echo "-----------------------------------------"

if command_exists fvwm; then
    if [ -f "$FVWM_CONFIG_DIR/.fvwm2rc" ]; then
        echo -n "Testing fvwm config syntax... "

        # fvwm doesn't have a built-in syntax checker, so we do a basic parse check
        if fvwm -c -f "$FVWM_CONFIG_DIR/.fvwm2rc" 2>&1 | grep -qi "error\|warning"; then
            echo -e "${RED}FAILED${NC}"
            fvwm -c -f "$FVWM_CONFIG_DIR/.fvwm2rc" 2>&1 | head -20
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN}OK${NC}"
        fi

        # Check if required files exist
        echo -n "Checking for required fvwm files... "
        MISSING_FILES=0
        for file in styles keybindings menus functions; do
            if [ ! -f "$FVWM_CONFIG_DIR/$file" ]; then
                echo -e "${RED}Missing: $file${NC}"
                MISSING_FILES=$((MISSING_FILES + 1))
            fi
        done

        if [ $MISSING_FILES -eq 0 ]; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${RED}$MISSING_FILES file(s) missing${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${RED}ERROR: .fvwm2rc not found at $FVWM_CONFIG_DIR${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}WARNING: fvwm not installed, skipping validation${NC}"
    echo "Install with: sudo apt-get install fvwm"
fi

echo ""

# ==================== Validate jwm Configuration ====================
echo "Validating jwm configuration..."
echo "-----------------------------------------"

if command_exists jwm; then
    if [ -f "$JWM_CONFIG" ]; then
        echo -n "Testing jwm config syntax... "

        # jwm has a built-in syntax checker with -p flag
        if jwm -p -f "$JWM_CONFIG" >/dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${RED}FAILED${NC}"
            echo "Errors:"
            jwm -p -f "$JWM_CONFIG" 2>&1 | head -20
            ERRORS=$((ERRORS + 1))
        fi

        # Check if it's valid XML
        echo -n "Validating XML structure... "
        if command_exists xmllint; then
            if xmllint --noout "$JWM_CONFIG" 2>/dev/null; then
                echo -e "${GREEN}OK${NC}"
            else
                echo -e "${RED}FAILED${NC}"
                xmllint --noout "$JWM_CONFIG" 2>&1 | head -20
                ERRORS=$((ERRORS + 1))
            fi
        else
            echo -e "${YELLOW}SKIPPED (xmllint not installed)${NC}"
        fi
    else
        echo -e "${RED}ERROR: .jwmrc not found at $JWM_CONFIG${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}WARNING: jwm not installed, skipping validation${NC}"
    echo "Install with: sudo apt-get install jwm"
fi

echo ""

# ==================== Validate JSON Configuration ====================
echo "Validating extracted JSON configuration..."
echo "-----------------------------------------"

JSON_CONFIG="$PROJECT_DIR/examples/lxde/extracted-config.json"

if [ -f "$JSON_CONFIG" ]; then
    echo -n "Checking JSON syntax... "
    if command_exists python3; then
        if python3 -c "import json; json.load(open('$JSON_CONFIG'))" 2>/dev/null; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${RED}FAILED${NC}"
            python3 -c "import json; json.load(open('$JSON_CONFIG'))" 2>&1
            ERRORS=$((ERRORS + 1))
        fi

        # Check for required keys
        echo -n "Checking for required keys... "
        MISSING_KEYS=0
        for key in desktops window_manager panel applications autostart keybindings; do
            if ! python3 -c "import json; config=json.load(open('$JSON_CONFIG')); assert '$key' in config" 2>/dev/null; then
                echo -e "${RED}Missing key: $key${NC}"
                MISSING_KEYS=$((MISSING_KEYS + 1))
            fi
        done

        if [ $MISSING_KEYS -eq 0 ]; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${YELLOW}WARNING: $MISSING_KEYS key(s) missing${NC}"
        fi
    else
        echo -e "${YELLOW}SKIPPED (python3 not found)${NC}"
    fi
else
    echo -e "${YELLOW}WARNING: Extracted JSON not found${NC}"
    echo "Run: python3 converters/lxde-extract.py <config-path> -o examples/lxde/extracted-config.json"
fi

echo ""

# ==================== Summary ====================
echo "========================================="
echo "  Validation Summary"
echo "========================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All validations passed!${NC}"
    echo ""
    echo "Configurations are ready to use."
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    echo ""
    echo "Please fix the errors above before using the configurations."
    exit 1
fi
