#!/usr/bin/env python3
"""
LXDE to JWM Converter

Converts LXDE configuration (in JSON format) to JWM configuration.
Generates a single .jwmrc XML file.
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


def openbox_key_to_jwm(ob_key):
    """Convert OpenBox key notation to JWM notation"""
    # Map: C=Control, A=Alt, S=Shift, W=Super
    key = ob_key
    mask_parts = []

    # Extract modifiers
    if 'C-' in key:
        mask_parts.append('C')
        key = key.replace('C-', '')
    if 'A-' in key:
        mask_parts.append('A')
        key = key.replace('A-', '')
    if 'S-' in key:
        mask_parts.append('S')
        key = key.replace('S-', '')
    if 'W-' in key:
        mask_parts.append('4')  # Super
        key = key.replace('W-', '')

    mask = ''.join(mask_parts) if mask_parts else ''

    return key, mask


def openbox_action_to_jwm(action, command=None):
    """Convert OpenBox action to JWM action"""
    action_map = {
        'Close': 'close',
        'ToggleShowDesktop': 'showdesktop',
        'DesktopLeft': 'ldesktop',
        'DesktopRight': 'rdesktop',
        'DesktopUp': 'udesktop',
        'DesktopDown': 'ddesktop',
        'SendToDesktopLeft': 'sendl',
        'SendToDesktopRight': 'sendr',
        'SendToDesktopUp': 'sendu',
        'SendToDesktopDown': 'sendd',
        'NextWindow': 'nextstacked',
        'PreviousWindow': 'prevstacked',
        'Lower': 'lower',
        'ShowMenu': 'root:1',
        'ToggleMaximizeFull': 'maximize',
        'ToggleFullscreen': 'fullscreen',
        'Iconify': 'minimize',
        'Execute': f'exec:{command}' if command else None
    }

    return action_map.get(action)


def prettify_xml(elem):
    """Return a pretty-printed XML string"""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def convert_to_jwm(json_file, output_file):
    """Main conversion function"""
    # Load JSON config
    with open(json_file, 'r') as f:
        config = json.load(f)

    # Create root JWM element
    jwm = ET.Element('JWM')
    jwm.append(ET.Comment(' Generated from LXDE configuration '))

    # ==================== Root Menu ====================
    root_menu = ET.SubElement(jwm, 'RootMenu', onroot='12')

    # Add terminal as first item
    if config.get('applications', {}).get('terminal'):
        terminal = config['applications']['terminal']
        prog = ET.SubElement(root_menu, 'Program', icon='utilities-terminal', label='Terminal')
        prog.text = terminal

    # Add applications submenu
    apps_menu = ET.SubElement(root_menu, 'Menu', icon='folder', label='Applications')

    # Categorize launchers
    if config.get('panel', {}).get('launchers'):
        launchers = config['panel']['launchers']
        categories = {
            'Web Browsers': [],
            'Development': [],
            'Office': [],
            'Graphics': [],
            'System Tools': [],
            'Databases': []
        }

        for launcher in launchers:
            if isinstance(launcher, dict):
                continue  # Skip weather/clock widgets

            launcher_lower = launcher.lower()

            if 'chromium' in launcher_lower or 'vivaldi' in launcher_lower or 'firefox' in launcher_lower:
                categories['Web Browsers'].append(launcher)
            elif 'netbeans' in launcher_lower or 'idea' in launcher_lower or 'cursor' in launcher_lower:
                categories['Development'].append(launcher)
            elif 'libreoffice' in launcher_lower:
                categories['Office'].append(launcher)
            elif 'gimp' in launcher_lower or 'gpicview' in launcher_lower or 'cheese' in launcher_lower:
                categories['Graphics'].append(launcher)
            elif 'dbeaver' in launcher_lower or 'dbschema' in launcher_lower or 'beekeeper' in launcher_lower:
                categories['Databases'].append(launcher)
            elif 'htop' in launcher_lower or 'lxtask' in launcher_lower or 'virt-manager' in launcher_lower:
                categories['System Tools'].append(launcher)

        # Add category submenus
        for category, items in categories.items():
            if items:
                cat_menu = ET.SubElement(apps_menu, 'Menu', label=category)
                for item in items:
                    app_name = item.replace('.desktop', '').replace('-', ' ').title()
                    prog = ET.SubElement(cat_menu, 'Program', label=app_name)
                    prog.text = f'gtk-launch {item}'

    # File manager
    if config.get('applications', {}).get('webbrowser'):
        prog = ET.SubElement(apps_menu, 'Program', icon='web-browser', label='Web Browser')
        prog.text = config['applications']['webbrowser']

    # System menu items
    ET.SubElement(root_menu, 'Separator')

    if config.get('applications', {}).get('lock'):
        prog = ET.SubElement(root_menu, 'Program', icon='lock', label='Lock Screen')
        prog.text = config['applications']['lock']

    ET.SubElement(root_menu, 'Separator')
    ET.SubElement(root_menu, 'Restart', label='Restart JWM', icon='reload')
    ET.SubElement(root_menu, 'Exit', label='Exit', confirm='true', icon='exit')

    # ==================== Tray Configuration ====================
    panel_config = config.get('panel', {})
    position = panel_config.get('position', 'bottom')
    height = panel_config.get('height', 30)
    autohide = panel_config.get('autohide', False)

    # Set tray position
    if position == 'bottom':
        tray = ET.SubElement(jwm, 'Tray', x='0', y='-1')
    elif position == 'top':
        tray = ET.SubElement(jwm, 'Tray', x='0', y='0')
    else:
        tray = ET.SubElement(jwm, 'Tray', x='0', y='-1')

    if autohide:
        tray.set('autohide', 'on')
        tray.set('delay', '1000')
    else:
        tray.set('autohide', 'off')

    tray.set('height', str(height))

    # Tray contents
    ET.SubElement(tray, 'TrayButton', label='Menu').text = 'root:1'
    ET.SubElement(tray, 'Spacer', width='2')
    ET.SubElement(tray, 'TrayButton', label='_').text = 'showdesktop'
    ET.SubElement(tray, 'Spacer', width='2')

    # Pager
    ET.SubElement(tray, 'Pager', labeled='true')

    # Task list
    ET.SubElement(tray, 'TaskList', maxwidth='256')

    # Dock
    ET.SubElement(tray, 'Dock')

    # Clock
    clock_elem = ET.SubElement(tray, 'Clock', format='%Y-%m-%d %H:%M')
    ET.SubElement(clock_elem, 'Button', mask='123').text = 'exec:xclock'

    # ==================== Window Styles ====================
    window_style = ET.SubElement(jwm, 'WindowStyle', decorations='motif')

    # Font from GTK config
    if config.get('gtk', {}).get('font'):
        font = config['gtk']['font']
        font_name, _, font_size = font.partition(' ')
        if font_size:
            ET.SubElement(window_style, 'Font').text = f'{font_name}-{font_size}:bold'
        else:
            ET.SubElement(window_style, 'Font').text = f'{font_name}-10:bold'
    else:
        ET.SubElement(window_style, 'Font').text = 'Sans-10:bold'

    ET.SubElement(window_style, 'Width').text = '4'
    ET.SubElement(window_style, 'Corner').text = '0'
    ET.SubElement(window_style, 'Foreground').text = '#FFFFFF'
    ET.SubElement(window_style, 'Background').text = '#555555'
    ET.SubElement(window_style, 'Opacity').text = '1.0'

    active = ET.SubElement(window_style, 'Active')
    ET.SubElement(active, 'Foreground').text = '#FFFFFF'
    ET.SubElement(active, 'Background').text = '#0077CC'
    ET.SubElement(active, 'Opacity').text = '1.0'

    # Tray style
    tray_style = ET.SubElement(jwm, 'TrayStyle', decorations='motif')
    ET.SubElement(tray_style, 'Font').text = 'Sans-10'
    ET.SubElement(tray_style, 'Background').text = '#333333'
    ET.SubElement(tray_style, 'Foreground').text = '#FFFFFF'
    ET.SubElement(tray_style, 'Opacity').text = '0.95'

    # TaskList style
    tasklist_style = ET.SubElement(jwm, 'TaskListStyle', list='all', group='true')
    ET.SubElement(tasklist_style, 'Font').text = 'Sans-10'
    ET.SubElement(tasklist_style, 'Foreground').text = '#FFFFFF'
    ET.SubElement(tasklist_style, 'Background').text = '#333333'

    active_task = ET.SubElement(tasklist_style, 'Active')
    ET.SubElement(active_task, 'Foreground').text = '#FFFFFF'
    ET.SubElement(active_task, 'Background').text = '#555555'

    # Pager style
    pager_style = ET.SubElement(jwm, 'PagerStyle')
    ET.SubElement(pager_style, 'Foreground').text = '#555555'
    ET.SubElement(pager_style, 'Background').text = '#333333'
    ET.SubElement(pager_style, 'Text').text = '#FFFFFF'

    active_pager = ET.SubElement(pager_style, 'Active')
    ET.SubElement(active_pager, 'Foreground').text = '#0077CC'
    ET.SubElement(active_pager, 'Background').text = '#004488'

    # Menu style
    menu_style = ET.SubElement(jwm, 'MenuStyle', decorations='motif')
    ET.SubElement(menu_style, 'Font').text = 'Sans-10'
    ET.SubElement(menu_style, 'Foreground').text = '#FFFFFF'
    ET.SubElement(menu_style, 'Background').text = '#333333'

    active_menu = ET.SubElement(menu_style, 'Active')
    ET.SubElement(active_menu, 'Foreground').text = '#FFFFFF'
    ET.SubElement(active_menu, 'Background').text = '#0077CC'

    ET.SubElement(menu_style, 'Opacity').text = '0.85'

    # ==================== Icon Paths ====================
    icon_paths = [
        '/usr/share/icons',
        '/usr/share/pixmaps',
        '/usr/local/share/icons'
    ]
    for path in icon_paths:
        ET.SubElement(jwm, 'IconPath').text = path

    # ==================== Virtual Desktops ====================
    desktops_config = config.get('desktops', {})
    desktop_count = desktops_config.get('count', 2)
    desktop_names = desktops_config.get('names', [])

    desktops = ET.SubElement(jwm, 'Desktops', width=str(desktop_count), height='1')

    # Add desktop names as comments (JWM doesn't support naming individual desktops in XML)
    if desktop_names:
        for i, name in enumerate(desktop_names):
            desktops.append(ET.Comment(f' Desktop {i}: {name} '))

    ET.SubElement(desktops, 'Background', type='solid').text = '#111111'

    # ==================== Focus Model ====================
    wm_config = config.get('window_manager', {})
    if wm_config.get('focus') == 'follow_mouse':
        ET.SubElement(jwm, 'FocusModel').text = 'sloppy'
    else:
        ET.SubElement(jwm, 'FocusModel').text = 'click'

    # ==================== Other Settings ====================
    ET.SubElement(jwm, 'DoubleClickSpeed').text = '400'
    ET.SubElement(jwm, 'DoubleClickDelta').text = '2'
    ET.SubElement(jwm, 'SnapMode', distance='10').text = 'border'
    ET.SubElement(jwm, 'MoveMode').text = 'opaque'
    ET.SubElement(jwm, 'ResizeMode').text = 'opaque'

    # ==================== Key Bindings ====================
    # Navigation keys (for menus)
    ET.SubElement(jwm, 'Key', key='Up').text = 'up'
    ET.SubElement(jwm, 'Key', key='Down').text = 'down'
    ET.SubElement(jwm, 'Key', key='Right').text = 'right'
    ET.SubElement(jwm, 'Key', key='Left').text = 'left'
    ET.SubElement(jwm, 'Key', key='Return').text = 'select'
    ET.SubElement(jwm, 'Key', key='Escape').text = 'escape'

    # Application keybindings
    if config.get('keybindings'):
        for kb in config['keybindings']:
            ob_key = kb.get('key')
            action = kb.get('action')
            command = kb.get('command')

            if ob_key and action:
                key, mask = openbox_key_to_jwm(ob_key)
                jwm_action = openbox_action_to_jwm(action, command)

                if jwm_action:
                    # Handle Desktop action with number
                    if action == 'Desktop' and 'F' in key:
                        desktop_num = key.replace('F', '')
                        try:
                            desk_idx = int(desktop_num) - 1
                            jwm_action = f'desktop{desk_idx + 1}'
                        except ValueError:
                            continue

                    if mask:
                        ET.SubElement(jwm, 'Key', mask=mask, key=key).text = jwm_action
                    else:
                        ET.SubElement(jwm, 'Key', key=key).text = jwm_action

    # ==================== Mouse Bindings ====================
    # Basic mouse bindings
    ET.SubElement(jwm, 'Mouse', context='root', button='4').text = 'ldesktop'
    ET.SubElement(jwm, 'Mouse', context='root', button='5').text = 'rdesktop'

    ET.SubElement(jwm, 'Mouse', context='title', button='1').text = 'move'
    ET.SubElement(jwm, 'Mouse', context='title', button='2').text = 'move'
    ET.SubElement(jwm, 'Mouse', context='title', button='3').text = 'window'
    ET.SubElement(jwm, 'Mouse', context='title', button='4').text = 'shade'
    ET.SubElement(jwm, 'Mouse', context='title', button='5').text = 'shade'
    ET.SubElement(jwm, 'Mouse', context='title', button='11').text = 'maximize'

    ET.SubElement(jwm, 'Mouse', context='border', button='1').text = 'resize'
    ET.SubElement(jwm, 'Mouse', context='border', button='2').text = 'move'

    ET.SubElement(jwm, 'Mouse', context='close', button='-1').text = 'close'
    ET.SubElement(jwm, 'Mouse', context='maximize', button='-1').text = 'maximize'
    ET.SubElement(jwm, 'Mouse', context='minimize', button='-1').text = 'minimize'

    # ==================== Startup Commands ====================
    if config.get('autostart'):
        for app in config['autostart']:
            if app and not app.startswith('lxpanel') and not app.startswith('pcmanfm'):
                ET.SubElement(jwm, 'StartupCommand').text = app

    # ==================== Write to file ====================
    xml_string = prettify_xml(jwm)

    # Remove extra blank lines
    lines = xml_string.split('\n')
    clean_lines = [lines[0]]  # Keep XML declaration
    for line in lines[1:]:
        if line.strip() or clean_lines[-1].strip():
            clean_lines.append(line)

    with open(output_file, 'w') as f:
        f.write('\n'.join(clean_lines))

    print(f"JWM configuration written to {output_file}", file=sys.stderr)
    print(f"To use: copy to ~/.jwmrc or run: jwm -f {output_file}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Convert LXDE configuration (JSON) to JWM'
    )
    parser.add_argument(
        'json_file',
        help='Input JSON file from lxde-extract.py'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output .jwmrc file',
        default='./jwmrc'
    )

    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"Error: {args.json_file} not found", file=sys.stderr)
        sys.exit(1)

    convert_to_jwm(args.json_file, args.output)


if __name__ == '__main__':
    main()
