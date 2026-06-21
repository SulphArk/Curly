#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

# --- CONFIGURATION DATA EXTRACTED FROM IMAGES ---

AUTOSTART_LUA = """-- Extra autostart processes.
o.launch_on_start("my-service")
"""

BINDINGS_LUA = """-- Application bindings.
o.bind("SUPER + RETURN", "Terminal", { omarchy = "terminal" })
o.bind("SUPER + ALT + RETURN", "Tmux", { omarchy = "terminal-tmux" })
o.bind("SUPER + SHIFT + RETURN", "Browser", { omarchy = "browser" })
o.bind("SUPER + SHIFT + F", "File manager", { omarchy = "nautilus" })
o.bind("SUPER + ALT + SHIFT + F", "File manager (cwd)", { omarchy = "nautilus-cwd" })
o.bind("SUPER + SHIFT + B", "Browser", { omarchy = "browser" })
o.bind("SUPER + SHIFT + ALT + B", "Browser (private)", { omarchy = "browser --private" })
o.bind("SUPER + SHIFT + M", "Music", { omarchy = "or-focus spotify" })
o.bind("SUPER + SHIFT + ALT + M", "Music TUI", { tui = "cliamp", focus = true })
o.bind("SUPER + SHIFT + N", "Editor", { omarchy = "editor" })
o.bind("SUPER + SHIFT + D", "Docker", { tui = "lazydocker" })
o.bind("SUPER + SHIFT + G", "Signal", { launch = "signal-desktop", focus = "^signal$" })
o.bind("SUPER + SHIFT + O", "Obsidian", { launch = "obsidian", focus = "^obsidian$" })
o.bind("SUPER + SHIFT + W", "Typora", { launch = "typora --enable-wayland-ime" })
o.bind("SUPER + SHIFT + SLASH", "Passwords", { launch = "1password" })

-- Web app bindings.
o.bind("SUPER + SHIFT + A", "ChatGPT", { webapp = "https://chatgpt.com" })
o.bind("SUPER + SHIFT + ALT + A", "Grok", { webapp = "https://grok.com" })
o.bind("SUPER + SHIFT + C", "Calendar", { webapp = "https://app.hey.com/calendar/weeks" })
o.bind("SUPER + SHIFT + E", "Email", { webapp = "https://app.hey.com" })
o.bind("SUPER + SHIFT + Y", "YouTube", { webapp = "https://youtube.com" })
o.bind("SUPER + SHIFT + ALT + G", "WhatsApp", { webapp = "https://web.whatsapp.com", focus = true })
o.bind("SUPER + SHIFT + CTRL + G", "Google Messages", { webapp = "https://messages.google.com/web/conversations", focus = true })
o.bind("SUPER + SHIFT + P", "Google Photos", { webapp = "https://photos.google.com", focus = true })
o.bind("SUPER + SHIFT + S", "Google Maps", { webapp = "https://maps.google.com", focus = true })
o.bind("SUPER + SHIFT + X", "X", { webapp = "https://x.com" })
o.bind("SUPER + SHIFT + ALT + X", "X Post", { webapp = "https://x.com/compose/post" })

-- Add extra bindings below.
-- o.bind("SUPER + SHIFT + R", "SSH", "alacritty -e ssh your-server")

-- Overwrite existing bindings with hl.unbind() first if needed.
-- hl.unbind("SUPER", "SPACE")
-- o.bind("SUPER + SPACE", "Omarchy menu", "omarchy-menu")

-- Logitech MX Keys examples:
-- o.bind("SUPER + SHIFT + S", nil, "omarchy-capture-screenshot")
-- o.bind("SUPER + H", nil, "woxtype record toggle")
-- o.bind("SUPER + PERIOD", nil, { omarchy = "walker -m symbols" })
"""

CONFIG_JSONC = """{
    "reload_style_on_change": true,
    "layer": "top",
    "position": "top",
    "spacing": 8,
    "height": 26,
    "width": 8,
    "modules-left": ["custom/omarchy", "hyprland/workspaces"],
    "modules-center": ["clock#horizontal", "clock#vertical", "custom/weather", "custom/update", "custom/waytxt", "custom/notification-silencing-indicator"],
    "modules-right": [
        "group/tray-expander",
        "bluetooth",
        "network",
        "pulseaudio",
        "cpu",
        "battery"
    ],
    "hyprland/workspaces": {
        "on-click": "activate",
        "format": "{icon}",
        "format-icons": {
            "default": "○",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            "10": "0",
            "active": "●"
        }
    },
    "persistent-workspaces": {
        "1": [],
        "2": [],
        "3": [],
        "4": [],
        "5": []
    },
    "custom/omarchy": {
        "format": "<span font='omarchy'>\\ue900</span>",
        "on-click": "omarchy-menu"
    }
}
"""

STYLE_CSS = """@import "../omarchy/current/theme/waybar.css";

* {
    background-color: @background;
    color: @foreground;
    border: none;
    border-radius: 0;
    min-height: 0;
    font-family: 'JetBrainsMono Nerd Font';
    font-size: 12px;
}

.modules-left {
    margin-left: 8px;
}

.modules-right {
    margin-right: 8px;
}

#workspaces button {
    all: initial;
    padding: 0 6px;
    margin: 0 1.5px;
    min-width: 9px;
}

#workspaces button.empty {
    opacity: 0.5;
}

#cpu,
#battery,
#pulseaudio,
#custom-omarchy,
#custom-update {
    min-width: 12px;
    margin: 0 7.5px;
}

#tray {
    margin-right: 16px;
}

#bluetooth {
    /* bluetooth custom styles */
}
"""

# --- INSTALLER LOGIC ---

DEPENDENCIES = [
    "hyprland", "waybar", "nautilus", "alacritty", 
    "jetbrains-mono-fonts-all", "git", "lua", "luajit"
]

def print_status(msg, success=True):
    prefix = "[✓]" if success else "[X]"
    print(f"{prefix} {msg}")

def install_dependencies():
    print("\n--> Installing system dependencies via DNF...")
    try:
        # Check if we have sudo privileges
        if os.geteuid() != 0:
            print("[!] This script requires root privileges to install packages. Escalating with sudo...")
            cmd_prefix = ["sudo"]
        else:
            cmd_prefix = []

        subprocess.run(cmd_prefix + ["dnf", "check-update"], stdout=subprocess.DEVNULL)
        subprocess.run(cmd_prefix + ["dnf", "install", "-y"] + DEPENDENCIES, check=True)
        print_status("All system dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install package dependencies: {e}", success=False)
        sys.exit(1)

def deploy_configs():
    print("\n--> Deploying configuration files...")
    home = Path.home()
    
    # Target directories
    hypr_dir = home / ".config" / "hypr"
    waybar_dir = home / ".config" / "waybar"
    
    # Create paths safely
    hypr_dir.mkdir(parents=True, exist_ok=True)
    waybar_dir.mkdir(parents=True, exist_ok=True)
    
    configs = {
        hypr_dir / "autostart.lua": AUTOSTART_LUA,
        hypr_dir / "bindings.lua": BINDINGS_LUA,
        waybar_dir / "config.jsonc": CONFIG_JSONC,
        waybar_dir / "style.css": STYLE_CSS
    }
    
    for path, content in configs.items():
        try:
            # Backup if file exists
            if path.exists():
                backup = path.with_suffix(path.suffix + ".bak")
                shutil.copy2(path, backup)
                print(f"    Backed up existing {path.name} to {backup.name}")
                
            with open(path, "w") as f:
                f.write(content)
            print_status(f"Wrote configuration to {path}")
        except Exception as e:
            print_status(f"Failed to write {path.name}: {e}", success=False)

def main():
    print("=========================================")
    print(" Standalone Hyprland & Waybar Installer  ")
    print("=========================================")
    
    # Run the setup steps
    install_dependencies()
    deploy_configs()
    
    print("\n=========================================")
    print(" Setup Complete! Restart Hyprland to apply.")
    print("=========================================")

if __name__ == "__main__":
    main()
