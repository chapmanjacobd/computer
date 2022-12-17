bass source /etc/profile
source ~/.config/fish/functions/ls.fish

set CLOUDSDK_PYTHON python3.9
set NPM_PACKAGES "$HOME/.npm-packages"
set PATH $PATH $NPM_PACKAGES/bin
fzf_configure_bindings --variables

bind \b backward-kill-bigword
bind \cy redo

