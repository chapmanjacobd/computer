bass source /etc/profile
source ~/.config/fish/functions/ls.fish

set CLOUDSDK_PYTHON python3.9
set NPM_PACKAGES "$HOME/.npm-packages"
set PATH $PATH $NPM_PACKAGES/bin
fzf_configure_bindings --variables

bind \e\[1\;5C forward-bigword
bind \e\[1\;5D backward-bigword
bind \b backward-kill-bigword
bind \cy redo
