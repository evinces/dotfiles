export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"

export ELECTRON_OZONE_PLATFORM_HINT "wayland"
export GDK_BACKEND="wayland"
export _JAVA_AWT_WM_NONREPARENTING="1"
export MOZ_ENABLE_WAYLAND="1"
export QT_AUTO_SCREEN_SCALE_FACTOR="1"
export QT_QPA_PLATFORM="wayland"
export QT_QPA_PLATFORMTHEME="qt6ct"
export QT_WAYLAND_DISABLE_WINDOWDECORATION="1"
export SDL_VIDEODRIVER="wayland"

export EDITOR="nvim"
export TERM="kitty"
export TERMINAL="$TERM"
export BROWSER="zen-browser"

export DOTFILES_HOME="$HOME/git/dotfiles"
export NIRI_SCRIPTS="$XDG_CONFIG_HOME/niri/scripts"

typeset -U path
path+="$NIRI_SCRIPTS"
path+="$HOME/.local/bin"
path+="$HOME/go/bin"
export PATH

export DATE=$(date "+A, %B %e  %_I:%M%P")
export FZF_DEFAULT_OPTS="--style minimal --color 16 --layout=reverse --height 30% --preview='bat -p --color=always {}'"
export FZF_CTRL_R_OPTS="--style minimal --color 16 --info inline --no-sort --no-preview"
export MANPAGER="less -R --use-color"
export LESS="R --use-color"
