# Defined interactively
function dl.torrents --wraps='lb'
    ~/.local/data/qbittorrent/queue/

    lb download --direct --cookies-from-browser firefox $argv
end
