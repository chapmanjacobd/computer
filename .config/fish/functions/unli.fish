# Defined in /tmp/fish.yTspbW/unli.fish @ line 2
function unli --description alias\ unli=ssh\ jacob@unli.xyz\ -t\ \'tmux\ a\ -t\ base\ \|\|\ tmux\ new\ -s\ base\'
    TERM=xterm ssh $argv jacob@unli.xyz -t 'abduco -A base bash'
end
