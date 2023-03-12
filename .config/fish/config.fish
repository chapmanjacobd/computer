bass source /etc/profile

set NPM_PACKAGES "$HOME/.npm-packages"
set PATH $PATH $NPM_PACKAGES/bin
fzf_configure_bindings --variables

bind \e\[1\;5C forward-bigword
bind \e\[1\;5D backward-bigword
bind \b backward-kill-bigword
bind \cy redo

source ~/.config/fish/functions/ls.fish

source $__fish_config_dir/abbreviations

function multicd
    echo (string repeat -n (math (string length -- $argv[1]) - 1) ../)
end
abbr --add dotdot --regex '^\.\.+$' --function multicd

function last_history_item; echo $history[1]; end
abbr -a !! --position anywhere --function last_history_item

function _abbr_zip
    echo zip -qr (datestamp).zip
end
abbr -a zip --function _abbr_zip
