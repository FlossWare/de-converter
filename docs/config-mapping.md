# LXDE/OpenBox to fvwm/jwm Configuration Mapping

This document provides a comprehensive mapping between LXDE/OpenBox configuration elements and their equivalents in fvwm and jwm window managers.

## Table of Contents

1. [Desktop/Workspace Management](#desktopworkspace-management)
2. [Window Manager Behavior](#window-manager-behavior)
3. [Key Bindings](#key-bindings)
4. [Mouse Bindings](#mouse-bindings)
5. [Panel/Tray Configuration](#paneltray-configuration)
6. [Window Styles and Themes](#window-styles-and-themes)
7. [Application Launchers](#application-launchers)
8. [Autostart Applications](#autostart-applications)

---

## Desktop/Workspace Management

### Desktop Count and Names

**LXDE/OpenBox** (`~/.config/openbox/lxde-rc.xml`):
```xml
<desktops>
  <number>2</number>
  <names>
    <name>Amanda</name>
    <name>Scot</name>
  </names>
</desktops>
```

**fvwm** (`~/.fvwm/.fvwm2rc`):
```
DesktopName 0 Amanda
DesktopName 1 Scot
DesktopSize 1x2
```

**jwm** (`~/.jwmrc`):
```xml
<Desktops width="2" height="1">
  <!-- Desktop 0: Amanda -->
  <!-- Desktop 1: Scot -->
  <Background type="solid">#111111</Background>
</Desktops>
```

**Notes:**
- OpenBox uses 1-based numbering displayed to users, but 0-based internally
- fvwm uses 0-based indexing
- jwm uses width × height grid layout
- JWM doesn't support named desktops in XML (only via comments)

---

## Window Manager Behavior

### Focus Model

**LXDE/OpenBox**:
```xml
<focus>
  <followMouse>yes</followMouse>
  <focusLast>yes</focusLast>
  <raiseOnFocus>no</raiseOnFocus>
</focus>
```

**fvwm**:
```
Style * SloppyFocus
Style * MouseFocusClickRaises
```

**jwm**:
```xml
<FocusModel>sloppy</FocusModel>
```

**Mapping:**

| OpenBox | fvwm | jwm |
|---------|------|-----|
| `followMouse=yes` | `SloppyFocus` | `<FocusModel>sloppy</FocusModel>` |
| `followMouse=no` | `ClickToFocus` | `<FocusModel>click</FocusModel>` |
| `raiseOnFocus=no` | `MouseFocusClickRaises` | N/A (implicit) |

### Window Placement

**LXDE/OpenBox**:
```xml
<placement>
  <policy>UnderMouse</policy>
  <center>yes</center>
</placement>
```

**fvwm**:
```
Style * MinOverlapPlacement
# or
Style * CascadePlacement
# or
Style * UnderMousePlacement
```

**jwm**:
```
# JWM doesn't have explicit placement policy configuration
# Windows are placed using internal algorithm
```

---

## Key Bindings

### Modifier Keys

**Notation:**

| Description | OpenBox | fvwm | jwm |
|-------------|---------|------|-----|
| Control | `C-` | `C` | `C` |
| Alt/Meta | `A-` | `M` | `A` |
| Shift | `S-` | `S` | `S` |
| Super/Win | `W-` | `4` | `4` |
| No modifier | - | `N` | (none) |

### Common Keybindings

#### Desktop Switching

**OpenBox**:
```xml
<keybind key="C-A-Left">
  <action name="DesktopLeft">
    <dialog>no</dialog>
    <wrap>no</wrap>
  </action>
</keybind>
```

**fvwm**:
```
Key Left A CM GotoDesk -1 0
```

**jwm**:
```xml
<Key mask="CA" key="Left">ldesktop</Key>
```

**Mapping Table:**

| OpenBox Action | fvwm Command | jwm Action |
|----------------|--------------|------------|
| `DesktopLeft` | `GotoDesk -1 0` | `ldesktop` |
| `DesktopRight` | `GotoDesk 1 0` | `rdesktop` |
| `DesktopUp` | `GotoDesk 0 -1` | `udesktop` |
| `DesktopDown` | `GotoDesk 0 1` | `ddesktop` |
| `Desktop <N>` | `GotoDesk 0 <N-1>` | `desktop<N>` |

#### Window Management

| OpenBox Action | fvwm Command | jwm Action |
|----------------|--------------|------------|
| `Close` | `Close` | `close` |
| `Iconify` | `Iconify` | `minimize` |
| `ToggleMaximizeFull` | `Maximize` | `maximize` |
| `ToggleFullscreen` | `Fullscreen` | `fullscreen` |
| `Lower` | `Lower` | `lower` |
| `Raise` | `Raise` | `raise` |
| `ToggleShade` | `WindowShade` | `shade` |

#### Window Switching

**OpenBox**:
```xml
<keybind key="A-Tab">
  <action name="NextWindow"/>
</keybind>
```

**fvwm**:
```
Key Tab A M Next (CurrentDesk, !Iconic) Focus
```

**jwm**:
```xml
<Key mask="A" key="Tab">nextstacked</Key>
```

#### Application Launching

**OpenBox**:
```xml
<keybind key="W-e">
  <action name="Execute">
    <command>pcmanfm</command>
  </action>
</keybind>
```

**fvwm**:
```
Key e A 4 Exec exec pcmanfm
```

**jwm**:
```xml
<Key mask="4" key="e">exec:pcmanfm</Key>
```

---

## Mouse Bindings

### Window Title Bar

**OpenBox**:
```xml
<context name="Titlebar">
  <mousebind button="Left" action="Drag">
    <action name="Move"/>
  </mousebind>
  <mousebind button="Left" action="DoubleClick">
    <action name="ToggleMaximizeFull"/>
  </mousebind>
</context>
```

**fvwm**:
```
Mouse 1 T N Move-or-Raise
Mouse 1 T D Maximize
```

**jwm**:
```xml
<Mouse context="title" button="1">move</Mouse>
<Mouse context="title" button="11">maximize</Mouse>
```

### Context Mapping

| OpenBox Context | fvwm Context | jwm Context |
|-----------------|--------------|-------------|
| `Titlebar` | `T` | `title` |
| `Frame` | `W` | `border` |
| `Root` | `R` | `root` |
| `Icon` | `I` | `icon` |
| `Close` | (button) | `close` |
| `Maximize` | (button) | `maximize` |
| `Iconify` | (button) | `minimize` |

### Button Mapping

| OpenBox | fvwm | jwm |
|---------|------|-----|
| `Left` | `1` | `1` |
| `Middle` | `2` | `2` |
| `Right` | `3` | `3` |
| `ScrollUp` | `4` | `4` |
| `ScrollDown` | `5` | `5` |
| `DoubleClick` | (action `D`) | `11` |

### Common Mouse Bindings

| Action | OpenBox | fvwm | jwm |
|--------|---------|------|-----|
| Move window | `A-Left drag` | `Mouse 1 W M Move` | Context-based |
| Resize window | `A-Right drag` | `Mouse 3 W M Resize` | Context-based |
| Root menu | `Right on root` | `Mouse 3 R A Menu RootMenu` | (automatic) |
| Lower window | `A-Middle` | `Mouse 2 W M Lower` | Context-based |

---

## Panel/Tray Configuration

### Panel Position and Size

**LXDE Panel** (`~/.config/lxpanel/LXDE/panels/panel`):
```
Global {
  edge=bottom
  align=center
  width=90
  height=30
  autohide=1
}
```

**fvwm** (FvwmButtons):
```
*ButtonBar: Geometry 800x30+0-0
*ButtonBar: Rows 1
*ButtonBar: Columns 20
```

**jwm**:
```xml
<Tray x="0" y="-1" height="30" autohide="on" delay="1000">
  ...
</Tray>
```

**Position Mapping:**

| LXDE edge | fvwm Geometry | jwm Tray |
|-----------|---------------|----------|
| `top` | `+0+0` | `y="0"` |
| `bottom` | `+0-0` | `y="-1"` |
| `left` | `+0+0` (vertical) | `x="0"` |
| `right` | `-0+0` (vertical) | `x="-1"` |

### Panel Components

**LXDE** uses plugins:
- `menu` - Application menu
- `launchbar` - Application launchers
- `taskbar` - Window list
- `pager` - Desktop switcher
- `dclock` - Clock
- `weather` - Weather widget

**fvwm** equivalents:
- Menu: `Menu RootMenu`
- Launchers: `*ButtonBar: (Title, Action)`
- Task list: `FvwmIconMan` or `FvwmTaskBar`
- Pager: `FvwmPager`
- Clock: `*ButtonBar: (Swallow "xclock")`

**jwm** equivalents:
```xml
<Tray>
  <TrayButton label="Menu">root:1</TrayButton>  <!-- Menu -->
  <Pager labeled="true"/>                        <!-- Pager -->
  <TaskList/>                                    <!-- Task list -->
  <Clock format="%H:%M"/>                        <!-- Clock -->
  <Dock/>                                        <!-- Application dock -->
</Tray>
```

---

## Window Styles and Themes

### Window Decorations

**LXDE/OpenBox**:
```xml
<theme>
  <name>Clearlooks-3.4</name>
  <titleLayout>NLIMC</titleLayout>
  <font place="ActiveWindow">
    <name>Droid Sans</name>
    <size>8</size>
    <weight>Bold</weight>
  </font>
</theme>
```

**fvwm**:
```
Style * Font "xft:Droid Sans:size=8:bold"
Style * BorderWidth 4, HandleWidth 4
Style * MWMDecor, MWMFunctions
Colorset 1 fg white, bg #555555
Colorset 2 fg white, bg #0077CC
Style * Colorset 1, HilightColorset 2
```

**jwm**:
```xml
<WindowStyle decorations="motif">
  <Font>Droid Sans-8:bold</Font>
  <Width>4</Width>
  <Foreground>#FFFFFF</Foreground>
  <Background>#555555</Background>
  <Active>
    <Foreground>#FFFFFF</Foreground>
    <Background>#0077CC</Background>
  </Active>
</WindowStyle>
```

### Title Layout

**OpenBox** `titleLayout="NLIMC"`:
- `N` = Icon
- `L` = Label/Title
- `I` = Iconify
- `M` = Maximize
- `C` = Close

**fvwm** uses:
```
Style * TitleAtTop
Style * Button 1, Button 2, Button 4, Button 6
# Buttons are positional and require manual configuration
```

**jwm** - buttons are automatically positioned based on decorations setting.

---

## Application Launchers

### Desktop Files

All three systems can launch applications via `.desktop` files.

**LXDE Panel**:
```
Button {
  id=terminator.desktop
}
```

**fvwm**:
```
AddToMenu ApplicationsMenu "Terminal" Exec exec gtk-launch terminator.desktop
```

**jwm**:
```xml
<Program label="Terminal">gtk-launch terminator.desktop</Program>
```

### Direct Commands

**OpenBox**:
```xml
<action name="Execute">
  <command>terminator</command>
</action>
```

**fvwm**:
```
Exec exec terminator
```

**jwm**:
```xml
<Program>terminator</Program>
<!-- or via keybinding -->
<Key>exec:terminator</Key>
```

---

## Autostart Applications

### Configuration

**LXDE** (`~/.config/lxsession/LXDE/autostart`):
```
@lxpanel --profile LXDE
@pcmanfm --desktop --profile LXDE
@xscreensaver -no-splash
```

**fvwm** (`~/.fvwm/.fvwm2rc`):
```
AddToFunc InitFunction
+ I Exec exec lxpanel --profile LXDE
+ I Exec exec pcmanfm --desktop --profile LXDE
+ I Exec exec xscreensaver -no-splash
```

**jwm** (`~/.jwmrc`):
```xml
<StartupCommand>lxpanel --profile LXDE</StartupCommand>
<StartupCommand>pcmanfm --desktop --profile LXDE</StartupCommand>
<StartupCommand>xscreensaver -no-splash</StartupCommand>
```

**Notes:**
- Remove `@` prefix from LXDE autostart entries
- fvwm uses `InitFunction` for autostart
- jwm uses `<StartupCommand>` elements
- All three support multiple autostart commands

---

## Summary Comparison

| Feature | LXDE/OpenBox | fvwm | jwm |
|---------|--------------|------|-----|
| Config format | XML + INI | Text | XML |
| Config files | Multiple | Multiple (modular) | Single file |
| Modularity | Built-in panels | External modules | Built-in tray |
| Customization | Medium | Very High | Medium |
| Learning curve | Low | High | Low-Medium |
| Desktop files | Yes (.desktop) | Yes (gtk-launch) | Yes (gtk-launch) |
| Themes | GTK + OpenBox | Manual colorsets | Manual styles |
| Documentation | Good | Extensive | Good |

---

## Conversion Notes

1. **Key notation**: Carefully translate modifier keys between systems
2. **Desktop numbering**: Watch for 0-based vs 1-based indexing
3. **Mouse buttons**: Double-click is handled differently in each system
4. **Paths**: Update icon paths to match system installation
5. **Modules**: fvwm requires explicit module loading
6. **Menus**: fvwm and jwm require manual menu construction
7. **Themes**: Visual appearance requires manual color/font mapping
8. **Weather widgets**: LXDE weather plugins have no direct equivalent

---

## Tools

This project provides three Python scripts:

1. **lxde-extract.py** - Extracts LXDE configuration to JSON
2. **lxde-to-fvwm.py** - Converts JSON to fvwm configs
3. **lxde-to-jwm.py** - Converts JSON to jwm config

### Usage

```bash
# Extract LXDE config
python3 lxde-extract.py ~/.config -o config.json

# Convert to fvwm
python3 lxde-to-fvwm.py config.json -o ~/fvwm-config

# Convert to jwm
python3 lxde-to-jwm.py config.json -o ~/.jwmrc
```

---

## References

- [LXDE Documentation](http://wiki.lxde.org/)
- [OpenBox Documentation](http://openbox.org/wiki/Help:Contents)
- [fvwm Documentation](https://fvwm.org/documentation/)
- [JWM Documentation](http://joewing.net/projects/jwm/)
