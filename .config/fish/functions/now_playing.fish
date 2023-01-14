function now_playing
    echo '{ "command": ["get_property", "path"] }' | socat - $MPV_SOCKET | jq -r .data
end
