# Defined via `source`
function pstop
    set pid (pgrep -fa $argv | fzf-choose | cut -d' ' -f1)
    echo kill -TERM $pid
    kill -HUP $pid
end
