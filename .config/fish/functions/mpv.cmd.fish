# Defined interactively
function mpv.cmd
    echo $argv | socat - $MPV_SOCKET | jq -r .data
end
