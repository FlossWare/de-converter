#!/usr/bin/env python3
"""
LXDE to FVWM Converter

Converts LXDE configuration (in JSON format) to FVWM configuration files.
Generates modular fvwm config: .fvwm2rc, functions, keybindings, menus, styles
"""

import argparse
import json
import os
import sys
from pathlib import Path


def openbox_key_to_fvwm(ob_key):
    """Convert OpenBox key notation to fvwm notation"""
    # Map: C=Ctrl, A=Alt/Meta, S=Shift, W=Super/Win
    fvwm_key = ob_key
    mods = []

    # Extract modifiers
    if 'C-' in fvwm_key:
        mods.append('C')
        fvwm_key = fvwm_key.replace('C-', '')
    if 'A-' in fvwm_key:
        mods.append('M')
        fvwm_key = fvwm_key.replace('A-', '')
    if 'S-' in fvwm_key:
        mods.append('S')
        fvwm_key = fvwm_key.replace('S-', '')
    if 'W-' in fvwm_key:
        mods.append('4')  # Super key
        fvwm_key = fvwm_key.replace('W-', '')

    mod_str = ''.join(mods) if mods else 'N'

    return fvwm_key, mod_str


def openbox_action_to_fvwm(action, command=None):
    """Convert OpenBox action to fvwm function"""
    action_map = {
        'Close': 'Close',
        'ToggleShowDesktop': 'ToggleShowDesktop',
        'DesktopLeft': 'GotoDesk -1 0',
        'DesktopRight': 'GotoDesk 1 0',
        'DesktopUp': 'GotoDesk 0 -1',
        'DesktopDown': 'GotoDesk 0 1',
        'SendToDesktopLeft': 'MoveToDesk -1 0',
        'SendToDesktopRight': 'MoveToDesk 1 0',
        'SendToDesktopUp': 'MoveToDesk 0 -1',
        'SendToDesktopDown': 'MoveToDesk 0 1',
        'Desktop': 'GotoDesk',
        'NextWindow': 'Next (CurrentDesk, !Iconic) Focus',
        'PreviousWindow': 'Prev (CurrentDesk, !Iconic) Focus',
        'Lower': 'Lower',
        'ShowMenu': 'Menu',
        'ToggleMaximizeFull': 'Maximize',
        'ToggleFullscreen': 'Fullscreen',
        'Iconify': 'Iconify',
        'Execute': f'Exec exec {command}' if command else 'Nop'
    }

    return action_map.get(action, 'Nop')


def generate_main_config(config, output_dir):
    """Generate main .fvwm2rc file"""
    lines = [
        "# FVWM Configuration",
        "# Generated from LXDE configuration",
        "",
        "# Set the image path for icons and images",
        "ImagePath /usr/share/icons:/usr/share/pixmaps:+",
        "",
        "# Read modular configs",
        f"Read {output_dir}/styles",
        f"Read {output_dir}/functions",
        f"Read {output_dir}/menus",
        f"Read {output_dir}/keybindings",
        "",
    ]

    # Desktop configuration
    if config.get('desktops'):
        desktops = config['desktops']
        lines.append("# Virtual Desktops")
        for i, name in enumerate(desktops.get('names', [])):
            lines.append(f"DesktopName {i} {name}")
        lines.append(f"DesktopSize 1x{desktops.get('count', 4)}")
        lines.append("")

    # Window manager behavior
    if config.get('window_manager'):
        wm = config['window_manager']
        lines.append("# Window Manager Behavior")

        if wm.get('focus') == 'follow_mouse':
            lines.append("Style * SloppyFocus")
        else:
            lines.append("Style * ClickToFocus")

        if not wm.get('raise_on_focus', False):
            lines.append("Style * MouseFocusClickRaises")

        lines.append("Style * DecorateTransient")
        lines.append("Style * NoPPosition")
        lines.append("")

    # Initialize modules
    lines.extend([
        "# Modules",
        "AddToFunc StartFunction",
        "+ I Module FvwmButtons ButtonBar",
        "+ I Module FvwmPager FvwmPager 0 1",
        "",
    ])

    # Autostart applications
    if config.get('autostart'):
        lines.append("# Autostart Applications")
        lines.append("AddToFunc InitFunction")
        for app in config['autostart']:
            if app and not app.startswith('lxpanel') and not app.startswith('pcmanfm'):
                lines.append(f"+ I Exec exec {app}")
        lines.append("")

    return '\n'.join(lines)


def generate_styles(config, output_dir):
    """Generate styles configuration"""
    lines = [
        "# FVWM Window Styles",
        "# Generated from LXDE configuration",
        "",
        "# Default style",
        "Style * BorderWidth 4, HandleWidth 4",
        "Style * MWMFunctions, MWMDecor, HintOverride",
        "Style * ResizeOpaque, OpaqueMove",
        "Style * IconBox 10 80 -10 -10, IconGrid 10 10, IconFill left top",
        "",
    ]

    # Apply theme if available
    if config.get('window_manager', {}).get('theme'):
        theme = config['window_manager']['theme']
        lines.append(f"# Theme: {theme}")

    # Apply GTK font if available
    if config.get('gtk', {}).get('font'):
        font = config['gtk']['font']
        font_name, _, font_size = font.partition(' ')
        if font_size:
            lines.append(f'Style * Font "xft:{font_name}:size={font_size}"')
        lines.append("")

    # Colorsets
    lines.extend([
        "# Colorsets",
        "Colorset 0 fg black, bg white",
        "Colorset 1 fg white, bg #555555",
        "Colorset 2 fg white, bg #0077CC",
        "",
        "# Window colors",
        "Style * Colorset 1, HilightColorset 2",
        "",
        "# FvwmPager style",
        "Style FvwmPager NoTitle, Sticky, WindowListSkip, CirculateSkip",
        "Style FvwmButtons NoTitle, Sticky, WindowListSkip, CirculateSkip",
        "",
    ])

    return '\n'.join(lines)


def generate_keybindings(config):
    """Generate keybindings configuration"""
    lines = [
        "# FVWM Key Bindings",
        "# Generated from LXDE configuration",
        "",
        "# Syntax: Key <keyname> <context> <modifier> <action>",
        "# Context: R=Root, W=Window, T=Title, I=Icon, A=All",
        "# Modifier: N=None, C=Ctrl, S=Shift, M=Meta/Alt, 4=Super",
        "",
    ]

    if config.get('keybindings'):
        for kb in config['keybindings']:
            key = kb.get('key')
            action = kb.get('action')
            command = kb.get('command')

            if key and action:
                fvwm_key, mods = openbox_key_to_fvwm(key)
                fvwm_action = openbox_action_to_fvwm(action, command)

                # Handle Desktop action with number
                if action == 'Desktop' and 'F' in fvwm_key:
                    desktop_num = fvwm_key.replace('F', '')
                    try:
                        desk_idx = int(desktop_num) - 1
                        fvwm_action = f'GotoDesk 0 {desk_idx}'
                    except ValueError:
                        pass

                lines.append(f"Key {fvwm_key} A {mods} {fvwm_action}")

    lines.append("")

    return '\n'.join(lines)


def generate_menus(config):
    """Generate menus configuration"""
    lines = [
        "# FVWM Menus",
        "# Generated from LXDE configuration",
        "",
        "# Root Menu",
        'AddToMenu RootMenu "Main Menu" Title',
    ]

    # Add application launchers from panel
    if config.get('panel', {}).get('launchers'):
        launchers = config['panel']['launchers']

        # Group launchers by category
        categories = {
            'System': [],
            'Terminal': [],
            'File Manager': [],
            'Web Browsers': [],
            'IDEs': [],
            'Databases': [],
            'Office': [],
            'Graphics': [],
            'Other': []
        }

        for launcher in launchers:
            if isinstance(launcher, dict):
                continue  # Skip weather/clock widgets

            launcher_lower = launcher.lower()

            if 'terminator' in launcher_lower or 'xterm' in launcher_lower:
                categories['Terminal'].append(launcher)
            elif 'pcmanfm' in launcher_lower or 'file' in launcher_lower:
                categories['File Manager'].append(launcher)
            elif 'chromium' in launcher_lower or 'vivaldi' in launcher_lower or 'firefox' in launcher_lower:
                categories['Web Browsers'].append(launcher)
            elif 'netbeans' in launcher_lower or 'idea' in launcher_lower or 'cursor' in launcher_lower:
                categories['IDEs'].append(launcher)
            elif 'dbeaver' in launcher_lower or 'dbschema' in launcher_lower or 'beekeeper' in launcher_lower:
                categories['Databases'].append(launcher)
            elif 'libreoffice' in launcher_lower:
                categories['Office'].append(launcher)
            elif 'gimp' in launcher_lower or 'gpicview' in launcher_lower:
                categories['Graphics'].append(launcher)
            elif 'lock' in launcher_lower or 'logout' in launcher_lower:
                categories['System'].append(launcher)
            else:
                categories['Other'].append(launcher)

        # Generate submenus
        for category, items in categories.items():
            if items:
                lines.append(f'+ "{category}" Popup {category}Menu')

        # System menu items
        lines.extend([
            '+ "" Nop',
            '+ "Restart FVWM" Restart',
            '+ "Quit FVWM" Quit',
            "",
        ])

        # Generate category submenus
        for category, items in categories.items():
            if not items:
                continue

            lines.append(f'AddToMenu {category}Menu "{category}" Title')
            for item in items:
                app_name = item.replace('.desktop', '').replace('-', ' ').title()
                lines.append(f'+ "{app_name}" Exec exec gtk-launch {item}')
            lines.append("")

    # Mouse binding for root menu
    lines.extend([
        "# Mouse bindings for menus",
        "Mouse 3 R A Menu RootMenu",
        "Mouse 2 R A Menu RootMenu",
        "",
    ])

    return '\n'.join(lines)


def generate_functions(config):
    """Generate functions configuration"""
    lines = [
        "# FVWM Functions",
        "# Generated from LXDE configuration",
        "",
        "# Window Movement Functions",
        "AddToFunc Move-or-Raise I Raise",
        "+ M Move",
        "+ D Lower",
        "",
        "AddToFunc Resize-or-Raise I Raise",
        "+ M Resize",
        "+ D Lower",
        "",
        "# Toggle Desktop Function",
        "AddToFunc ToggleShowDesktop",
        "+ I All (CurrentPage, !Iconic, !Sticky) Iconify on",
        "+ I TestRc (Match) Break",
        "+ I All (CurrentPage, Iconic, !Sticky) Iconify off",
        "",
    ]

    return '\n'.join(lines)


def generate_fvwmbuttons_config(config):
    """Generate FvwmButtons module configuration"""
    lines = [
        "# FvwmButtons Configuration",
        "",
        "*ButtonBar: Geometry 800x30+0-0",
        "*ButtonBar: Rows 1",
        "*ButtonBar: Columns 20",
        "*ButtonBar: Frame 1",
        "*ButtonBar: Padding 2 2",
        "*ButtonBar: Font 7x13",
        "",
    ]

    # Add pager
    lines.append('*ButtonBar: (3x1, Swallow "FvwmPager" "FvwmPager 0 1")')

    # Add some common launchers
    if config.get('applications'):
        apps = config['applications']

        if apps.get('terminal'):
            lines.append(f'*ButtonBar: (Title Terminal, Action (Mouse 1) Exec exec {apps["terminal"]})')

        if apps.get('webbrowser'):
            lines.append(f'*ButtonBar: (Title Browser, Action (Mouse 1) Exec exec {apps["webbrowser"]})')

    lines.append("")

    return '\n'.join(lines)


def convert_to_fvwm(json_file, output_dir):
    """Main conversion function"""
    # Load JSON config
    with open(json_file, 'r') as f:
        config = json.load(f)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate all config files
    configs = {
        '.fvwm2rc': generate_main_config(config, output_dir),
        'styles': generate_styles(config, output_dir),
        'keybindings': generate_keybindings(config),
        'menus': generate_menus(config),
        'functions': generate_functions(config),
    }

    # Write all files
    for filename, content in configs.items():
        filepath = output_path / filename
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Created: {filepath}", file=sys.stderr)

    print(f"\nFVWM configuration generated in {output_dir}", file=sys.stderr)
    print(f"To use: copy {output_dir}/.fvwm2rc and other files to ~/.fvwm/", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Convert LXDE configuration (JSON) to FVWM'
    )
    parser.add_argument(
        'json_file',
        help='Input JSON file from lxde-extract.py'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output directory for fvwm configs',
        default='./fvwm-config'
    )

    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"Error: {args.json_file} not found", file=sys.stderr)
        sys.exit(1)

    convert_to_fvwm(args.json_file, args.output)


if __name__ == '__main__':
    main()
