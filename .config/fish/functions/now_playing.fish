# Defined interactively
function now_playing
    cat /tmp/catt_playing
    echo '{ "command": ["get_property", "path"] }' | socat - /tmp/mpv_socket | jq -r .data
end
