set CLOUDSDK_PYTHON python3.9
bass source /etc/profile.d/flatpak.sh /etc/profile.d/kde.sh /etc/profile.d/vte.sh
bass 'eval "$(dircolors)"'
set NPM_PACKAGES "$HOME/.npm-packages"
set PATH $PATH $NPM_PACKAGES/bin
set MANPATH $NPM_PACKAGES/share/man $MANPATH
fzf_configure_bindings --variables
bind \b backward-kill-bigword
complete -f -k -c mvlj -c reddit-links-update -c reddit-add -c dl-get-sounds -c dl-get-videos -c dl-get-photos -a "(__fish_complete_directories ~/d/ DFOLDER | sed 's|/home/xk/d/\(.*\)/|\1|' )"
complete -f -k -c reddit-add -c dl-get-sounds -c dl-get-videos -c dl-get-photos -a "(cat ~/mc/*reddit.txt)"
