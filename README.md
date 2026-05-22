# de-converter

**Desktop Environment Configuration Converter**

Convert desktop environment configurations to lightweight window manager configurations. This project provides tools to extract settings from various desktop environments (LXDE, XFCE, KDE, etc.) and generate equivalent configurations for window managers like fvwm, jwm, i3, and others.

> *Your desktop environment, on any window manager.*

## Overview

Desktop environments like LXDE, XFCE, and KDE provide complete user experiences but can be resource-intensive. This project helps you migrate your carefully configured desktop environment setup to lightweight standalone window managers while preserving your settings, keybindings, and workflows.

### Currently Supported

- **LXDE** → fvwm, jwm (full support)
- More converters coming soon (XFCE, KDE, MATE)

### Features

- **Extract LXDE configuration** from multiple config files to a unified JSON format
- **Generate fvwm configuration** with modular config files (keybindings, menus, styles, functions)
- **Generate jwm configuration** as a single XML file
- **Preserve settings**:
  - Desktop names and layout
  - Keybindings and mouse bindings
  - Application launchers
  - Panel/tray configuration
  - Window manager behavior (focus model, placement)
  - Autostart applications
  - GTK theme and font settings

## Project Structure

```
de-converter/
├── README.md                    # This file
├── docs/
│   ├── config-mapping.md       # LXDE mapping documentation
│   └── freebsd-compatibility.md
├── converters/
│   ├── lxde/                   # LXDE converters
│   │   ├── lxde-extract.py    # Extract LXDE configs to JSON
│   │   ├── lxde-to-fvwm.py    # Convert JSON to fvwm config
│   │   └── lxde-to-jwm.py     # Convert JSON to jwm config
│   ├── xfce/                   # XFCE converters (future)
│   └── kde/                    # KDE converters (future)
├── examples/
│   ├── lxde/                   # Extracted LXDE configs (JSON)
│   ├── fvwm/                   # Generated fvwm configs
│   │   ├── .fvwm2rc           # Main fvwm config
│   │   ├── functions          # Function definitions
│   │   ├── keybindings        # Key bindings
│   │   ├── menus              # Menu definitions
│   │   └── styles             # Window styles
│   └── jwm/
│       └── .jwmrc             # Generated jwm config
└── tests/
    └── validate-configs.sh     # Config validation script
```

## Requirements

### Python Dependencies

- Python 3.6 or higher
- Standard library modules only (no external packages required):
  - `xml.etree.ElementTree` - XML parsing
  - `configparser` - INI file parsing
  - `json` - JSON processing
  - `argparse` - Command-line argument parsing

### Optional Tools

- **fvwm** - For running and validating fvwm configs
- **jwm** - For running and validating jwm configs
- **xmllint** - For XML validation (jwm config)

#### Installation

**Debian/Ubuntu:**
```bash
sudo apt-get install fvwm jwm libxml2-utils
```

**FreeBSD:**
```bash
sudo pkg install fvwm jwm libxml2
```

> **Note**: See [docs/freebsd-compatibility.md](docs/freebsd-compatibility.md) for FreeBSD-specific instructions and path adjustments.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/FlossWare/de-converter.git
cd de-converter

# Extract your LXDE config
python3 converters/lxde/lxde-extract.py ~/.config -o config.json -p

# Convert to your preferred window manager
python3 converters/lxde/lxde-to-fvwm.py config.json -o ~/fvwm-config
# or
python3 converters/lxde/lxde-to-jwm.py config.json -o ~/.jwmrc
```

## Usage

### Step 1: Extract Desktop Environment Configuration

#### For LXDE

Extract your LXDE configuration to JSON format:

```bash
python3 converters/lxde/lxde-extract.py ~/.config -o config.json -p
```

Or extract from a backup:
```bash
python3 converters/lxde/lxde-extract.py /path/to/backup/.config -o config.json -p
```

Options:
- `-o, --output`: Output JSON file (default: stdout)
- `-p, --pretty`: Pretty-print JSON output

The extracted JSON contains:
- Desktop configuration (names, count)
- Window manager settings (focus model, theme, placement)
- Keybindings and mouse bindings
- Panel configuration (position, launchers, widgets)
- Default applications
- Autostart programs

### Step 2a: Convert to fvwm

Generate fvwm configuration files:

```bash
python3 converters/lxde/lxde-to-fvwm.py config.json -o ~/fvwm-config
```

This creates:
- `.fvwm2rc` - Main configuration file
- `styles` - Window styles and decorations
- `keybindings` - Keyboard shortcuts
- `menus` - Application menus
- `functions` - Custom functions

Copy to your home directory:
```bash
mkdir -p ~/.fvwm
cp ~/fvwm-config/* ~/.fvwm/
```

### Step 2b: Convert to jwm

Generate jwm configuration:

```bash
python3 converters/lxde/lxde-to-jwm.py config.json -o ~/.jwmrc
```

This creates a single `.jwmrc` XML configuration file.

### Step 3: Validate Configurations

Run the validation script to check for syntax errors:

```bash
bash tests/validate-configs.sh
```

This validates:
- fvwm configuration syntax
- jwm configuration syntax and XML structure
- JSON extraction completeness

### Step 4: Test Your New Configuration

#### Testing fvwm

Start a new X session with fvwm:
```bash
# From console
startx -- :1

# Or add to ~/.xsession:
exec fvwm
```

Or test without logging out:
```bash
Xephyr :1 -screen 1024x768 &
DISPLAY=:1 fvwm
```

#### Testing jwm

Start a new X session with jwm:
```bash
# From console
startx /usr/bin/jwm -- :1

# Or add to ~/.xsession:
exec jwm
```

Or test with Xephyr:
```bash
Xephyr :1 -screen 1024x768 &
DISPLAY=:1 jwm
```

## Examples

This repository includes pre-generated examples from an actual LXDE configuration:

- **2 Desktops**: "Amanda" and "Scot"
- **Follow-mouse focus**
- **Bottom panel** with autohide
- **Application launchers** organized by category:
  - System tools
  - Terminals
  - Web browsers
  - IDEs (NetBeans, IntelliJ IDEA)
  - Databases (DBeaver, DbSchema, Beekeeper Studio)
  - Office (LibreOffice suite)
  - Graphics (GIMP, GPicView)
- **Common keybindings**:
  - `Ctrl+Alt+Arrows` - Switch desktops
  - `Alt+F4` - Close window
  - `Alt+Tab` - Switch windows
  - `Win+e` - File manager
  - `Print` - Screenshot

View the generated configs:
- fvwm: `examples/fvwm/`
- jwm: `examples/jwm/.jwmrc`

## Configuration Mapping

See [docs/config-mapping.md](docs/config-mapping.md) for comprehensive documentation on how LXDE/OpenBox settings map to fvwm and jwm.

Key mappings include:

| Feature | LXDE/OpenBox | fvwm | jwm |
|---------|--------------|------|-----|
| Desktop switching | `C-A-Left` | `Key Left A CM GotoDesk -1 0` | `<Key mask="CA" key="Left">ldesktop</Key>` |
| Close window | `A-F4` | `Key F4 A M Close` | `<Key mask="A" key="F4">close</Key>` |
| Focus model | `followMouse=yes` | `SloppyFocus` | `<FocusModel>sloppy</FocusModel>` |

## Customization

The generated configurations are starting points. You can customize them further:

### fvwm Customization

Edit the modular config files in `~/.fvwm/`:
- **styles** - Change colors, fonts, borders
- **keybindings** - Add/modify keyboard shortcuts
- **menus** - Customize application menus
- **functions** - Create custom functions

Reload configuration: `FvwmCommand Restart` or `Ctrl+Alt+Backspace` (if configured)

### jwm Customization

Edit `~/.jwmrc`:
- Modify `<WindowStyle>` for appearance
- Add/change `<Key>` bindings
- Update `<Program>` entries in menus
- Adjust `<Tray>` configuration

Reload configuration: `jwm -restart` or right-click → Restart

## Troubleshooting

### Extraction Issues

**Problem**: "Config files not found"
- **Solution**: Ensure the path points to a directory containing `.config/lxsession`, `.config/openbox`, etc.

**Problem**: Empty JSON output
- **Solution**: Check that LXDE config files exist and are readable

### fvwm Issues

**Problem**: "Read: command not found"
- **Solution**: Ensure the path in `.fvwm2rc` points to correct config directory

**Problem**: Modules don't start
- **Solution**: Check that FvwmButtons and FvwmPager are installed with fvwm

### jwm Issues

**Problem**: "Parse error in config"
- **Solution**: Run `jwm -p -f ~/.jwmrc` to see specific error, validate XML with `xmllint`

**Problem**: Icons not showing
- **Solution**: Update `<IconPath>` entries in `.jwmrc` to match your system

## Roadmap

### Desktop Environments
- [x] LXDE
- [ ] XFCE
- [ ] KDE Plasma
- [ ] MATE
- [ ] Cinnamon

### Window Managers
- [x] fvwm
- [x] jwm
- [ ] i3/sway
- [ ] awesome
- [ ] dwm
- [ ] bspwm

## Contributing

Contributions welcome! Areas for improvement:

- **New converters** - XFCE, KDE, MATE support
- **Additional WMs** - i3, awesome, bspwm output formats
- **Better theme mapping** - Improved color/font conversion
- **Testing** - More test cases and validation
- **Documentation** - Usage examples, video tutorials
- **GUI** - Visual configuration tool

See the LXDE converters in `converters/lxde/` as reference implementations.

## License

This project is provided as-is for educational and practical use.

## Resources

### Desktop Environments
- [LXDE Documentation](http://wiki.lxde.org/)
- [XFCE Documentation](https://docs.xfce.org/)
- [KDE Documentation](https://docs.kde.org/)

### Window Managers
- [fvwm Official Site](https://fvwm.org/)
- [JWM Official Site](http://joewing.net/projects/jwm/)
- [i3 User's Guide](https://i3wm.org/docs/userguide.html)
- [awesome WM](https://awesomewm.org/)

### OpenBox
- [OpenBox Documentation](http://openbox.org/wiki/Help:Contents) (LXDE's WM)

## Credits

Created to facilitate migration from full desktop environments to lightweight window managers while preserving familiar configurations and workflows.

## Author

**Scot P. Floess**
- GitHub: [@sfloess](https://github.com/sfloess)

## Version

Current version: 1.0.0

## Changelog

### 1.0.0 (2026-05-21)
- Initial release
- LXDE configuration extraction
- fvwm configuration generation
- jwm configuration generation
- Configuration mapping documentation
- Validation script
- FreeBSD compatibility
