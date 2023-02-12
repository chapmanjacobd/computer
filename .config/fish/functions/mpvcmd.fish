# Defined interactively
function mpvcmd
    echo $argv | socat - $MPV_SOCKET | jq -r .data
end
