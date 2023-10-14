# Defined via `source`
function parallel-stop
    kill -HUP (pgrep -fa parallel | fzf-choose | cut -d' ' -f1)
end
