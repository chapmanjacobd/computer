# Defined interactively
function dl_torrents
    ~/.local/data/qbittorrent/queue/

    lb links --cookies-from-browser firefox $argv --no-extract --download
end
