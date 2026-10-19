# Defined interactively
function dl.torrents
    ~/.local/data/qbittorrent/queue/

    lb download --direct --cookies-from-browser firefox $argv
end
