# Defined in /tmp/fish.2H3azM/nextSong.fish @ line 2
function nextSong
    kdialog --passivepopup 'just use alt+t boyyyyyeeee' 2
    #catt stop &
    #set song (echo '{ "command": ["get_property", "path"] }' | socat - /tmp/mpv_socket | jq -r .data)
    #echo 'playlist_next force' | socat - /tmp/mpv_socket
    #incrFileSuffix $song
end
