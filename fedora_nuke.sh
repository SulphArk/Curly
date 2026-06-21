#!/usr/bin/env bash
# =============================================================================
# fedora_nuke.sh
# Run as root. Fully unattended.
# Removes everything graphical except Wayland + Pipewire.
# Boots to TTY. You install what you want after.
# =============================================================================

set -euo pipefail

[[ $EUID -ne 0 ]] && { echo "Run as root: su - then ./fedora_nuke.sh"; exit 1; }

G='\033[0;32m'; Y='\033[1;33m'; C='\033[0;36m'; B='\033[1m'; R='\033[0m'

step() { echo -e "\n${C}${B}==> $*${R}"; }
ok()   { echo -e "${G}    done.${R}"; }

echo -e "${B}"
echo "╔══════════════════════════════════════╗"
echo "║         Fedora Nuclear Reset         ║"
echo "║   Keeps: Wayland + Pipewire only     ║"
echo "╚══════════════════════════════════════╝"
echo -e "${R}"
echo -e "${Y}Starting in 5 seconds — Ctrl+C to abort...${R}"
sleep 5

# ── 1. Update ─────────────────────────────────────────────────────────────────
step "Updating system"
dnf upgrade -y --refresh -q
ok

# ── 2. Remove DE groups ───────────────────────────────────────────────────────
step "Removing desktop environment groups"
DE_GROUPS=(
    "GNOME"
    "KDE Plasma Workspaces"
    "Xfce Desktop"
    "Cinnamon Desktop"
    "MATE Desktop"
    "LXDE Desktop"
    "LXQt Desktop"
    "Budgie Desktop"
    "Basic Desktop"
    "Workstation Environment"
    "gnome-desktop"
    "kde-desktop"
    "xfce-desktop"
    "cinnamon-desktop"
    "mate-desktop"
    "lxde-desktop"
    "lxqt-desktop"
    "budgie-desktop"
    "basic-desktop"
    "workstation-product-environment"
)

for group in "${DE_GROUPS[@]}"; do
    dnf group remove -y "$group" &>/dev/null && echo "  removed: $group" || true
done
ok

# ── 3. Remove everything graphical ───────────────────────────────────────────
step "Removing all DEs, WMs, display managers, Xorg, apps"
dnf remove -y \
    gnome-shell gnome-session gnome-control-center gnome-terminal \
    gnome-software gdm nautilus mutter gnome-keyring \
    plasma-desktop plasma-workspace sddm kde-connect \
    xfce4-session xfwm4 xfce4-panel thunar \
    cinnamon muffin nemo \
    mate-session-manager marco caja \
    lxde-common openbox pcmanfm \
    lxqt-session budgie-desktop deepin-desktop \
    lightdm lxdm \
    xorg-x11-server-Xorg xorg-x11-xinit xorg-x11-drv-* \
    pulseaudio pulseaudio-libs \
    firefox chromium \
    libreoffice* \
    totem rhythmbox shotwell eog evince \
    gedit geany \
    2>/dev/null || true
ok

# ── 4. Autoremove orphans ─────────────────────────────────────────────────────
step "Removing orphaned dependencies"
dnf autoremove -y -q
ok

# ── 5. Set boot to TTY ───────────────────────────────────────────────────────
step "Setting boot target to TTY"
systemctl set-default multi-user.target
for dm in gdm sddm lightdm lxdm; do
    systemctl disable "$dm" 2>/dev/null || true
done
ok

# ── 6. Install only what you said: base tools + Wayland + Pipewire ────────────
step "Installing base tools, Wayland, Pipewire"
dnf install -y \
    bash-completion \
    vim-enhanced \
    git \
    curl wget \
    python3 python3-pip \
    htop tmux \
    tar unzip \
    man-db \
    net-tools iproute \
    NetworkManager \
    wayland-protocols \
    wayland-devel \
    pipewire \
    pipewire-alsa \
    pipewire-pulseaudio \
    pipewire-jack-audio-connection-kit \
    wireplumber \
    polkit \
    2>/dev/null
ok

# ── 7. Clean cache ────────────────────────────────────────────────────────────
step "Cleaning dnf cache"
dnf clean all -q
ok

echo
echo -e "${G}${B}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  Done. Nothing but TTY, Wayland, and Pipewire.      ║"
echo "║  Build from here however you want.                  ║"
echo "║                                                      ║"
echo "║  Rebooting in 60 seconds — Ctrl+C to cancel.        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${R}"

sleep 60 && reboot
