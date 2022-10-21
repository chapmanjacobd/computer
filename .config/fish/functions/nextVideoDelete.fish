function nextVideoDelete
    set song (echo '{ "command": ["get_property", "path"] }' | socat - /tmp/mpvsocket | jq -r .data)
    /bin/rm (files /home/xk/Videos/tron/ | fileTypeVideos | head -1)
    echo "$song"
    echo quit | socat - /tmp/mpvsocket
end
