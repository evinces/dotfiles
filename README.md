# dotfiles

A collection of dot files for my personal desktop and laptop.

## Install Prep

### Wi-Fi Connection

```bash
iwctl
[iwctl] # station wlan0 connect '<WIFI SSID>'
[iwctl] > Password: <WIFI PASSWORD>
[iwctl] # exit
ping -c 3 archlinux.org
```

### Archinstall Configuration

#### Base System & Kernel

* Kernel: `linux-zen`
* Microcode: `amd-ucode`

#### Graphics Drivers

* Desktop: `nvidia-dkms`, `nvidia-settings`, `nvidia-utils`
* Laptop: `mesa`, `vulkan-radeon`, `xf86-video-amdgpu`

#### Audio Subsystem

* Server: `pipewire`, `pipewire-alsa`, `pipewire-jack`, `pipewire-pulse`, `wireplumber`, `libpulse`

#### Core Graphical Environment

* Compositor: `niri`, `xorg-xwayland`
* Interface: `waybar`, `fuzzel`, `mako`, `swaybg`, `swayidle`, `gtklock`
* Greeter: `greetd`, `greetd-regreet`
* Network: `networkmanager`, `network-manager-applet`, `blueman`, `bluez`, `bluez-utils`

## Post-Install

```bash
# 1. Set wireless regulatory domain
sudo pacman -S wireless-regdb
sudo vim /etc/conf.d/wireless-regdom
> # Uncomment WIRELESS_REGDOM="US"

# 2. Enable pacman colors
sudo vim /etc/pacman.conf
> # Uncomment Color

# 3. Version control 
sudo pacman -S git jujutsu base-devel
jj config set --user user.name "<NAME>"
jj config set --user user.email "<EMAIL>"
export GIT_HOME="${GIT_HOME:-$HOME/git}"
mkdir -p $GIT_HOME

# 4. Authentication (SSH)
ssh-keygen -t ed25519 -C "<EMAIL>"
cat ~/.ssh/id_ed25519.pub
# Action: Copy the output and add it to [GitHub Settings > SSH and GPG Keys](https://github.com/settings/keys).

# 5. Clone Dotfiles
jj git clone git@github.com:evinces/dots.git $GIT_HOME/dots
cd $GIT_HOME/dots
./make-links.py

# 6. Clone & install paru
jj git clone https://aur.archlinux.org/paru-bin.git $GIT_HOME/paru-bin
cd $GIT_HOME/paru-bin
makepkg -si
paru --gendb

# 7. Shell Environment
paru -S zsh kitty starship eza bat
chsh -s /usr/bin/zsh
mkdir -p $HOME/.cache/zsh

# 8. Reboot to cleanly load Configuration
reboot
```

## Desktop Environment

```bash
# Theming & Fonts
paru -S rose-pine-cursor wallust
paru -S qt5-wayland qt6-wayland qt6ct
paru -S noto-fonts-cjk noto-fonts-emoji noto-fonts-extra otf-font-awesome
paru -S ttf-victor-mono-nerd ttf-nerd-fonts-symbols ttf-noto-nerd

# Utilities
paru -S ripgrep 7zip bemoji btop chafa fastfetch fd fzf grim slurp
paru -S man-db man-pages rsync smartmontools
paru -S unzip usage wget wl-clipboard zram-generator
paru -S 1password
```

## Applications

```bash
# Browsers & Communication
paru -S discord proton-vpn-gtk-app evince
paru -S chromium zen-browser-bin helium-browser-bin

# Development
paru -S mise uv nvim jq lazygit jdk-openjdk docker docker-buildx

# Audio & Video
paru -S vlc easyeffects pavucontrol qpwgraph
paru -S calf lsp-plugins-lv2 zam-plugins-lv2 mda.lv2
paru -S gst-plugins-base gst-plugins-good gst-plugins-ugly gst-plugins-bad

# Gaming
paru -S steam gamescope proton-ge-custom-bin umu-launcher winetricks wine wine-gecko wine-mono 
```

## Hardware Specifics

### Desktop

```bash
# Nvidia Drivers & Utils
paru -S nvidia-dkms nvidia-settings nvtop libva-nvidia-driver

# Audio Interface (Focusrite)
paru -S alsa-scarlett-gui

# Streaming & Creative
paru -S obs-studio-git blender godot godot-mono krita streamdeck-ui openrgb openhue-cli
```

### Laptop

```bash
# Fingerprint Reader
paru -S fprintd brightnessctl
# Enroll fingerprints
fprintd-enroll

# Update PAM for fingerprint auth
sudo -e /etc/pam.d/system-local-login
> auth    sufficient pam_unix.so try_first_pass likeauth nullok
> auth    sufficient pam_fprintd.so
> auth    include    system-login
```
