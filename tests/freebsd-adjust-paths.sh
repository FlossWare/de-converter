#!/bin/sh
# FreeBSD Path Adjustment Script
# Converts Linux paths to FreeBSD paths in generated configs

FVWM_DIR="${1:-examples/fvwm}"
JWM_FILE="${2:-examples/jwm/.jwmrc}"

echo "========================================="
echo "  FreeBSD Path Adjustment Script"
echo "========================================="
echo ""

# Function to adjust paths in a file
adjust_file() {
    file="$1"

    if [ ! -f "$file" ]; then
        echo "Warning: $file not found, skipping"
        return
    fi

    # Create backup
    cp "$file" "$file.bak"

    # Adjust paths
    sed -i '' -e 's|/usr/share/icons|/usr/local/share/icons|g' \
              -e 's|/usr/share/pixmaps|/usr/local/share/pixmaps|g' \
              -e 's|/usr/share/applications|/usr/local/share/applications|g' \
              -e 's|/usr/share/lxde|/usr/local/share/lxde|g' \
              -e 's|/usr/bin/vivaldi-stable|/usr/local/bin/vivaldi-stable|g' \
              -e 's|/usr/bin/chromium|/usr/local/bin/chromium|g' \
              -e 's|/usr/bin/firefox|/usr/local/bin/firefox|g' \
              -e 's|exec /usr/bin/|exec /usr/local/bin/|g' \
              -e 's|Exec exec /usr/bin/|Exec exec /usr/local/bin/|g' \
              "$file"

    echo "  ✓ Adjusted: $(basename $file)"
}

# Adjust fvwm configs
if [ -d "$FVWM_DIR" ]; then
    echo "Adjusting fvwm configurations in $FVWM_DIR..."
    echo ""

    for file in "$FVWM_DIR"/*; do
        if [ -f "$file" ]; then
            adjust_file "$file"
        fi
    done

    echo ""
else
    echo "Warning: fvwm directory $FVWM_DIR not found"
    echo ""
fi

# Adjust jwm config
if [ -f "$JWM_FILE" ]; then
    echo "Adjusting jwm configuration: $JWM_FILE..."
    echo ""
    adjust_file "$JWM_FILE"
    echo ""
else
    echo "Warning: jwm config $JWM_FILE not found"
    echo ""
fi

echo "========================================="
echo "  Summary"
echo "========================================="
echo ""
echo "Path adjustments complete!"
echo "Original files backed up with .bak extension"
echo ""
echo "Changes made:"
echo "  /usr/share/*        → /usr/local/share/*"
echo "  /usr/bin/*          → /usr/local/bin/*"
echo "  (for common applications)"
echo ""
echo "Next steps:"
echo "  1. Review the adjusted configs"
echo "  2. Validate with: jwm -p -f $JWM_FILE"
echo "  3. Copy to home: cp -r $FVWM_DIR ~/.fvwm/"
echo "  4. Copy to home: cp $JWM_FILE ~/.jwmrc"
echo ""
