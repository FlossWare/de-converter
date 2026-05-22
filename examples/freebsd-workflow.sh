#!/bin/sh
# FreeBSD Complete Workflow Example
# This script demonstrates the complete workflow for FreeBSD users

echo "========================================="
echo "  LXDE to fvwm/jwm Converter"
echo "  FreeBSD Workflow"
echo "========================================="
echo ""

# Configuration
LXDE_CONFIG_DIR="${HOME}/.config"
OUTPUT_JSON="config.json"
FVWM_OUTPUT_DIR="fvwm-config"
JWM_OUTPUT_FILE="jwmrc"

echo "Step 1: Extracting LXDE configuration..."
echo "-----------------------------------------"
python3 converters/lxde/lxde-extract.py "$LXDE_CONFIG_DIR" -o "$OUTPUT_JSON" -p
echo ""

echo "Step 2: Converting to fvwm..."
echo "-----------------------------------------"
python3 converters/lxde/lxde-to-fvwm.py "$OUTPUT_JSON" -o "$FVWM_OUTPUT_DIR"
echo ""

echo "Step 3: Converting to jwm..."
echo "-----------------------------------------"
python3 converters/lxde/lxde-to-jwm.py "$OUTPUT_JSON" -o "$JWM_OUTPUT_FILE"
echo ""

echo "Step 4: Adjusting paths for FreeBSD..."
echo "-----------------------------------------"
sh tests/freebsd-adjust-paths.sh "$FVWM_OUTPUT_DIR" "$JWM_OUTPUT_FILE"
echo ""

echo "Step 5: Validating configurations..."
echo "-----------------------------------------"

# Validate jwm (if available)
if command -v jwm >/dev/null 2>&1; then
    echo -n "Validating jwm config... "
    if jwm -p -f "$JWM_OUTPUT_FILE" >/dev/null 2>&1; then
        echo "OK"
    else
        echo "FAILED"
        jwm -p -f "$JWM_OUTPUT_FILE"
    fi
else
    echo "jwm not installed, skipping validation"
    echo "Install with: sudo pkg install jwm"
fi

echo ""

echo "========================================="
echo "  Installation Instructions"
echo "========================================="
echo ""
echo "To install fvwm configuration:"
echo "  mkdir -p ~/.fvwm"
echo "  cp -r $FVWM_OUTPUT_DIR/* ~/.fvwm/"
echo ""
echo "To install jwm configuration:"
echo "  cp $JWM_OUTPUT_FILE ~/.jwmrc"
echo ""
echo "To use fvwm, add to ~/.xinitrc:"
echo "  exec /usr/local/bin/fvwm"
echo ""
echo "To use jwm, add to ~/.xinitrc:"
echo "  exec /usr/local/bin/jwm"
echo ""
echo "========================================="
echo "  Complete!"
echo "========================================="
