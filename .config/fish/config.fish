set CLOUDSDK_PYTHON python3.9
bass source /etc/profile
#bass 'eval "$(dircolors)"'
set NPM_PACKAGES "$HOME/.npm-packages"
set PATH $PATH $NPM_PACKAGES/bin
fzf_configure_bindings --variables
bind \b backward-kill-bigword
bind \cy redo

