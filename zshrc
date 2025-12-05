# .zshrc
bindkey -e

# history
SAVEHIST=1000000
HISTSIZE=1000000
HISTFILE="$XDG_CACHE_HOME/zsh/.histfile"
setopt append_history inc_append_history share_history hist_ignore_dups hist_ignore_space

# changing directories
setopt autocd

# expansion and globbing
setopt extended_glob glob_dots

# completion
autoload -U compinit && compinit
setopt auto_menu auto_param_slash menu_complete
zstyle ':completion:*' cache-path "$XDG_CACHE_HOME/zsh/zcompcache"
zstyle ':completion:*' menu select
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS} ma=0\;33
zstyle ':completion:*' file-list true
zstyle ':completion:*' squeeze-slashes false

# aliases
## defaults
alias cp='cp --archive --sparse=auto'
alias df='df --human-readable'
alias du='du --human-readable --max-depth=1'
alias eza='eza --long --header --icons --group-directories-first --git'
alias fastfetch='fastfetch --logo-recache'
alias grep='grep --color=auto'
alias ls='eza'
alias lsa='ls --all'
alias lt='eza --tree --level=3'
alias lta='lt --all'
alias umu-run='PROTONPATH="GE-Proton" umu-run'
alias vim='nvim'

## abbreviations
alias c='clear'
alias cff='clear && fastfetch'
alias ff='fastfetch'
alias k='kill'
alias ka='killall'
alias p='ps aux | grep'
alias wp='wallpaper.py'
alias g='git'
alias ga='git add'
# gc overwrites graph count
alias gc='git commit'
# gs overwrites ghostscript
alias gs='git status'
alias gd='git diff'
alias gp='git push'
alias gu='git pull'

# startup
source <(fzf --zsh)
source <(COMPLETE=zsh jj)
eval "$(starship init zsh)"
eval "$(mise activate zsh)"

fastfetch
