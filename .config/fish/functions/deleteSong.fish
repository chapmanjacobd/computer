function deleteSong
    set song (echo '{ "command": ["get_property", "path"] }' | socat - /tmp/mpvsocket | jq .data | sed -e 's/^"//' -e 's/"$//')

    echo playlist_next | socat - /tmp/mpvsocket
    trash $song
end
