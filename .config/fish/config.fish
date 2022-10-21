set CLOUDSDK_PYTHON python3.9
bass source /etc/profile.d/flatpak.sh /etc/profile.d/kde.sh /etc/profile.d/vte.sh
bass 'eval "$(dircolors)"'
set NPM_PACKAGES "$HOME/.npm-packages"
set PATH $PATH $NPM_PACKAGES/bin
set MANPATH $NPM_PACKAGES/share/man $MANPATH
fzf_configure_bindings --variables
bind \b backward-kill-bigword
