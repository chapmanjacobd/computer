# Defined via `source`
function parallel-stop
    set pid (pgrep -fa parallel | fzf.choose | cut -d' ' -f1)
    echo kill -TERM $pid
    kill -HUP $pid
end
