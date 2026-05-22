#!/usr/bin/env python3
"""
LXDE Configuration Extractor

Extracts configuration from LXDE config files and outputs JSON.
Parses: lxsession, openbox, lxpanel, and pcmanfm configurations.
"""

import argparse
import configparser
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_lxsession_config(config_path):
    """Parse lxsession desktop.conf (INI format)"""
    desktop_conf = config_path / "lxsession" / "LXDE" / "desktop.conf"
    config = {}

    if not desktop_conf.exists():
        return config

    parser = configparser.ConfigParser()
    parser.read(desktop_conf)

    # Extract default applications
    if parser.has_section('Session'):
        config['applications'] = {}
        for key, value in parser.items('Session'):
            if key.endswith('/command'):
                app_type = key.replace('/command', '').replace('_manager', '')
                config['applications'][app_type] = value

    # Extract GTK theme
    if parser.has_section('GTK'):
        config['gtk'] = {
            'theme': parser.get('GTK', 'sNet/ThemeName', fallback=''),
            'icon_theme': parser.get('GTK', 'sNet/IconThemeName', fallback=''),
            'font': parser.get('GTK', 'sGtk/FontName', fallback='')
        }

    return config


def parse_autostart(config_path):
    """Parse lxsession autostart file"""
    autostart_file = config_path / "lxsession" / "LXDE" / "autostart"
    autostart = []

    if not autostart_file.exists():
        return autostart

    with open(autostart_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove @ prefix if present
                if line.startswith('@'):
                    line = line[1:]
                autostart.append(line)

    return autostart


def parse_openbox_xml(config_path):
    """Parse OpenBox lxde-rc.xml configuration"""
    ob_config = config_path / "openbox" / "lxde-rc.xml"
    config = {}

    if not ob_config.exists():
        return config

    try:
        tree = ET.parse(ob_config)
        root = tree.getroot()

        # Remove namespace if present
        if root.tag.startswith('{'):
            ns = {'ob': root.tag.split('}')[0].strip('{')}
        else:
            ns = {}

        # Extract desktop configuration
        desktops = root.find('.//desktops') or root.find('.//{*}desktops')
        if desktops is not None:
            number_elem = desktops.find('number') or desktops.find('{*}number')
            names_elem = desktops.find('names') or desktops.find('{*}names')

            config['desktops'] = {
                'count': int(number_elem.text) if number_elem is not None else 4,
                'names': []
            }

            if names_elem is not None:
                for name_elem in names_elem.findall('name') or names_elem.findall('{*}name'):
                    if name_elem.text:
                        config['desktops']['names'].append(name_elem.text)

        # Extract focus configuration
        focus = root.find('.//focus') or root.find('.//{*}focus')
        if focus is not None:
            follow_mouse = focus.find('followMouse') or focus.find('{*}followMouse')
            raise_on_focus = focus.find('raiseOnFocus') or focus.find('{*}raiseOnFocus')

            config['window_manager'] = {
                'focus': 'follow_mouse' if (follow_mouse is not None and follow_mouse.text == 'yes') else 'click',
                'raise_on_focus': raise_on_focus.text == 'yes' if raise_on_focus is not None else False
            }

        # Extract placement configuration
        placement = root.find('.//placement') or root.find('.//{*}placement')
        if placement is not None:
            policy = placement.find('policy') or placement.find('{*}policy')
            if policy is not None and 'window_manager' in config:
                config['window_manager']['placement'] = policy.text.lower()

        # Extract theme
        theme = root.find('.//theme') or root.find('.//{*}theme')
        if theme is not None:
            name = theme.find('name') or theme.find('{*}name')
            if name is not None:
                if 'window_manager' not in config:
                    config['window_manager'] = {}
                config['window_manager']['theme'] = name.text

        # Extract keyboard bindings
        keyboard = root.find('.//keyboard') or root.find('.//{*}keyboard')
        if keyboard is not None:
            config['keybindings'] = []
            for keybind in keyboard.findall('.//keybind') or keyboard.findall('.//{*}keybind'):
                key = keybind.get('key')
                action_elem = keybind.find('.//action') or keybind.find('.//{*}action')
                if action_elem is not None:
                    action = action_elem.get('name')
                    command_elem = action_elem.find('command') or action_elem.find('{*}command')
                    command = command_elem.text if command_elem is not None else None

                    config['keybindings'].append({
                        'key': key,
                        'action': action,
                        'command': command
                    })

        # Extract mouse bindings
        mouse = root.find('.//mouse') or root.find('.//{*}mouse')
        if mouse is not None:
            config['mouse_bindings'] = []
            for mousebind in mouse.findall('.//mousebind') or mouse.findall('.//{*}mousebind'):
                button = mousebind.get('button')
                context = mousebind.get('context')
                action_type = mousebind.get('action')
                action_elem = mousebind.find('.//action') or mousebind.find('.//{*}action')
                if action_elem is not None:
                    action = action_elem.get('name')
                    config['mouse_bindings'].append({
                        'button': button,
                        'context': context,
                        'action_type': action_type,
                        'action': action
                    })

    except ET.ParseError as e:
        print(f"Warning: Could not parse OpenBox XML: {e}", file=sys.stderr)

    return config


def parse_lxpanel_config(config_path):
    """Parse lxpanel panel configuration"""
    panel_config = config_path / "lxpanel" / "LXDE" / "panels" / "panel"
    config = {}

    if not panel_config.exists():
        return config

    with open(panel_config, 'r') as f:
        content = f.read()

    # Parse Global section
    global_match = re.search(r'Global\s*{([^}]+)}', content, re.DOTALL)
    if global_match:
        global_content = global_match.group(1)
        config['panel'] = {}

        # Extract position
        edge_match = re.search(r'edge=(\w+)', global_content)
        if edge_match:
            config['panel']['position'] = edge_match.group(1)

        # Extract height
        height_match = re.search(r'height=(\d+)', global_content)
        if height_match:
            config['panel']['height'] = int(height_match.group(1))

        # Extract autohide
        autohide_match = re.search(r'autohide=(\d+)', global_content)
        if autohide_match:
            config['panel']['autohide'] = autohide_match.group(1) == '1'

        # Extract icon size
        iconsize_match = re.search(r'iconsize=(\d+)', global_content)
        if iconsize_match:
            config['panel']['iconsize'] = int(iconsize_match.group(1))

    # Parse Plugin sections (launchers)
    config['panel']['launchers'] = []
    plugin_sections = re.findall(r'Plugin\s*{([^}]+(?:{[^}]+}[^}]+)*)}', content, re.DOTALL)

    for plugin in plugin_sections:
        plugin_type_match = re.search(r'type=(\w+)', plugin)
        if plugin_type_match:
            plugin_type = plugin_type_match.group(1)

            if plugin_type == 'launchbar':
                # Extract buttons from launchbar
                buttons = re.findall(r'Button\s*{[^}]*id=([^\s}]+)', plugin)
                for button in buttons:
                    config['panel']['launchers'].append(button)
            elif plugin_type == 'weather':
                # Extract weather configuration
                city_match = re.search(r'city=([^\n]+)', plugin)
                if city_match:
                    config['panel']['launchers'].append({
                        'type': 'weather',
                        'city': city_match.group(1).strip('"')
                    })
            elif plugin_type == 'dclock':
                # Extract clock configuration
                fmt_match = re.search(r'ClockFmt=([^\n]+)', plugin)
                config['panel']['launchers'].append({
                    'type': 'clock',
                    'format': fmt_match.group(1) if fmt_match else '%H:%M'
                })

    return config


def extract_lxde_config(config_path):
    """Main extraction function - combines all parsers"""
    config_path = Path(config_path)

    result = {
        'source': str(config_path),
        'desktops': {},
        'window_manager': {},
        'panel': {},
        'applications': {},
        'autostart': [],
        'keybindings': [],
        'mouse_bindings': []
    }

    # Parse each config file
    lxsession_data = parse_lxsession_config(config_path)
    autostart_data = parse_autostart(config_path)
    openbox_data = parse_openbox_xml(config_path)
    lxpanel_data = parse_lxpanel_config(config_path)

    # Merge data
    if 'applications' in lxsession_data:
        result['applications'] = lxsession_data['applications']

    if 'gtk' in lxsession_data:
        result['gtk'] = lxsession_data['gtk']

    result['autostart'] = autostart_data

    if 'desktops' in openbox_data:
        result['desktops'] = openbox_data['desktops']

    if 'window_manager' in openbox_data:
        result['window_manager'] = openbox_data['window_manager']

    if 'keybindings' in openbox_data:
        result['keybindings'] = openbox_data['keybindings']

    if 'mouse_bindings' in openbox_data:
        result['mouse_bindings'] = openbox_data['mouse_bindings']

    if 'panel' in lxpanel_data:
        result['panel'] = lxpanel_data['panel']

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Extract LXDE configuration to JSON format'
    )
    parser.add_argument(
        'config_path',
        help='Path to .config directory (e.g., ~/.config or backup path)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file (default: stdout)',
        default=None
    )
    parser.add_argument(
        '-p', '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )

    args = parser.parse_args()

    # Extract configuration
    config = extract_lxde_config(args.config_path)

    # Output JSON
    if args.pretty:
        json_output = json.dumps(config, indent=2, sort_keys=True)
    else:
        json_output = json.dumps(config, sort_keys=True)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(json_output)
        print(f"Configuration written to {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == '__main__':
    main()
