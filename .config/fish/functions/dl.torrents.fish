# Defined interactively
function dl.torrents
    ~/.local/data/qbittorrent/queue/

    lb links --cookies-from-browser firefox $argv --no-extract --download
end
