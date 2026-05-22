# FreeBSD Compatibility Guide

This document covers using the LXDE to fvwm/jwm converters on FreeBSD.

## Compatibility Status

✅ **Fully Compatible** - The converter scripts work on FreeBSD with minimal adjustments.

### What Works As-Is

1. **Python scripts** - All three converters use only Python standard library
2. **LXDE config extraction** - Config file paths are the same (`~/.config/`)
3. **Configuration formats** - XML, INI, and JSON parsing work identically
4. **Window managers** - fvwm and jwm are available on FreeBSD

### What Needs Adjustment

1. **Installation paths** - FreeBSD uses `/usr/local` instead of `/usr` for packages
2. **Package manager** - Use `pkg` instead of `apt-get`
3. **Shell scripts** - Bash is not default (uses `/bin/sh`)

---

## Installation

### Install Python 3

FreeBSD usually comes with Python, but if needed:

```bash
# Using pkg (binary packages)
sudo pkg install python3

# Or using ports
cd /usr/ports/lang/python3
sudo make install clean
```

### Install Window Managers

```bash
# Install fvwm
sudo pkg install fvwm

# Install jwm
sudo pkg install jwm

# Install LXDE (if not already installed)
sudo pkg install lxde-meta
```

### Install Optional Tools

```bash
# For XML validation
sudo pkg install libxml2

# For bash (if validation script needs it)
sudo pkg install bash
```

---

## Path Differences

### Icon Paths

On FreeBSD, icons are typically in `/usr/local/share/`:

**Generated fvwm config:**
```
ImagePath /usr/local/share/icons:/usr/local/share/pixmaps:+
```

**Generated jwm config:**
```xml
<IconPath>/usr/local/share/icons</IconPath>
<IconPath>/usr/local/share/pixmaps</IconPath>
```

### Desktop Files

Desktop application launchers are in:
- `/usr/local/share/applications/` (instead of `/usr/share/applications/`)

### Executables

User-installed applications are in:
- `/usr/local/bin/` (instead of `/usr/bin/`)

---

## Path Adjustment Script

Create a script to update paths for FreeBSD:

```bash
#!/bin/sh
# freebsd-adjust-paths.sh
# Adjust generated configs for FreeBSD paths

FVWM_DIR="${1:-examples/fvwm}"
JWM_FILE="${2:-examples/jwm/.jwmrc}"

echo "Adjusting paths for FreeBSD..."

# Update fvwm configs
if [ -f "$FVWM_DIR/.fvwm2rc" ]; then
    echo "Updating fvwm config..."
    sed -i.bak 's|/usr/share|/usr/local/share|g' "$FVWM_DIR/.fvwm2rc"
    sed -i.bak 's|/usr/bin/|/usr/local/bin/|g' "$FVWM_DIR/.fvwm2rc"
    
    for file in "$FVWM_DIR"/*; do
        [ -f "$file" ] && sed -i.bak 's|/usr/share|/usr/local/share|g' "$file"
        [ -f "$file" ] && sed -i.bak 's|/usr/bin/|/usr/local/bin/|g' "$file"
    done
fi

# Update jwm config
if [ -f "$JWM_FILE" ]; then
    echo "Updating jwm config..."
    sed -i.bak 's|/usr/share|/usr/local/share|g' "$JWM_FILE"
    sed -i.bak 's|/usr/bin/|/usr/local/bin/|g' "$JWM_FILE"
fi

echo "Done! Original files saved with .bak extension"
```

Usage:
```bash
chmod +x freebsd-adjust-paths.sh
./freebsd-adjust-paths.sh examples/fvwm examples/jwm/.jwmrc
```

---

## Running the Converters on FreeBSD

The Python scripts work identically:

```bash
# Extract LXDE config
python3 converters/lxde-extract.py ~/.config -o config.json -p

# Convert to fvwm
python3 converters/lxde-to-fvwm.py config.json -o ~/fvwm-config

# Convert to jwm
python3 converters/lxde-to-jwm.py config.json -o ~/.jwmrc
```

---

## Validation Script

The validation script uses bash-specific features. Two options:

### Option 1: Use Bash

```bash
# Install bash
sudo pkg install bash

# Run validation with bash
bash tests/validate-configs.sh
```

### Option 2: Use FreeBSD sh

The script should mostly work with FreeBSD's `/bin/sh`, but if you encounter issues, modify the shebang:

```bash
#!/bin/sh
```

And replace bash arrays with compatible syntax.

---

## FreeBSD-Specific Considerations

### 1. Application Paths

Some applications may have different paths on FreeBSD:

```bash
# Linux path in LXDE config
/usr/bin/vivaldi-stable

# FreeBSD equivalent
/usr/local/bin/vivaldi-stable
```

The path adjustment script handles this automatically.

### 2. Desktop Files Location

If desktop files aren't found:

```bash
# Find desktop files
find /usr/local/share/applications -name "*.desktop"

# Manually update application launchers in generated configs
```

### 3. X Session Configuration

On FreeBSD, X session configuration might be in:
- `~/.xinitrc` (when using startx)
- `~/.xsession` (when using display manager)
- `/usr/local/etc/X11/xinit/xinitrc` (system default)

Example `~/.xinitrc`:
```bash
#!/bin/sh

# Start fvwm
exec /usr/local/bin/fvwm

# Or for jwm
# exec /usr/local/bin/jwm
```

### 4. Fonts

FreeBSD font paths:
- System fonts: `/usr/local/share/fonts/`
- User fonts: `~/.local/share/fonts/`

If fonts are missing:
```bash
# Install common fonts
sudo pkg install dejavu liberation-fonts-ttf
```

---

## Complete FreeBSD Workflow

```bash
# 1. Install dependencies
sudo pkg install python3 fvwm jwm libxml2

# 2. Clone/download this project
cd ~/wm-de

# 3. Extract LXDE config
python3 converters/lxde-extract.py ~/.config -o config.json -p

# 4. Generate fvwm config
python3 converters/lxde-to-fvwm.py config.json -o ~/fvwm-config

# 5. Generate jwm config
python3 converters/lxde-to-jwm.py config.json -o ~/.jwmrc.new

# 6. Adjust paths for FreeBSD
sed -i.bak 's|/usr/share|/usr/local/share|g' ~/fvwm-config/*
sed -i.bak 's|/usr/bin/|/usr/local/bin/|g' ~/fvwm-config/*
sed -i.bak 's|/usr/share|/usr/local/share|g' ~/.jwmrc.new
sed -i.bak 's|/usr/bin/|/usr/local/bin/|g' ~/.jwmrc.new

# 7. Copy to final locations
mkdir -p ~/.fvwm
cp ~/fvwm-config/* ~/.fvwm/
mv ~/.jwmrc.new ~/.jwmrc

# 8. Validate
jwm -p -f ~/.jwmrc

# 9. Test in Xephyr (if available)
pkg install xephyr
Xephyr :1 -screen 1024x768 &
DISPLAY=:1 jwm

# Or add to ~/.xinitrc and restart X
```

---

## Known Issues and Workarounds

### Issue 1: gtk-launch Not Found

Some FreeBSD systems may not have `gtk-launch` by default.

**Workaround**: Install gtk3
```bash
sudo pkg install gtk3
```

Or manually edit configs to use direct application paths instead of `gtk-launch desktop-file`.

### Issue 2: Icon Themes Not Found

**Workaround**: Install icon themes
```bash
sudo pkg install gnome-icon-theme
sudo pkg install hicolor-icon-theme
```

### Issue 3: Menu Icons Not Showing in JWM

**Workaround**: Update `<IconPath>` in `.jwmrc`:
```xml
<IconPath>/usr/local/share/icons/hicolor</IconPath>
<IconPath>/usr/local/share/pixmaps</IconPath>
<IconPath>/usr/local/share/icons</IconPath>
```

---

## Testing

Test generated configs before committing:

```bash
# Test fvwm config (dry run)
fvwm -f ~/.fvwm/.fvwm2rc -cmd "Echo Testing; Quit"

# Test jwm config (parse only)
jwm -p -f ~/.jwmrc
```

---

## Additional Resources

### FreeBSD Documentation
- [FreeBSD Handbook - X11](https://docs.freebsd.org/en/books/handbook/x11/)
- [FreeBSD Ports Collection](https://www.freebsd.org/ports/)

### Window Manager Resources
- [fvwm on FreeBSD](https://www.freshports.org/x11-wm/fvwm/)
- [jwm on FreeBSD](https://www.freshports.org/x11-wm/jwm/)

### Packages
- Search packages: `pkg search keyword`
- Package info: `pkg info packagename`
- List files: `pkg info -l packagename`

---

## Summary

| Feature | Linux | FreeBSD | Adjustment Needed |
|---------|-------|---------|-------------------|
| Python scripts | ✅ Works | ✅ Works | None |
| Config extraction | ✅ Works | ✅ Works | None |
| Generated configs | ✅ Works | ⚠️ Works | Path updates |
| Icon paths | `/usr/share` | `/usr/local/share` | sed or manual |
| Binary paths | `/usr/bin` | `/usr/local/bin` | sed or manual |
| Validation | bash | sh or bash | Install bash or modify |

**Bottom Line**: The converters work perfectly on FreeBSD. Just update paths from `/usr/` to `/usr/local/` in the generated configs.
