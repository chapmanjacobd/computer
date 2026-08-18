# Defined interactively
function torrent.size
    torrent.promote $argv -n 999999 -p | cut -d'#' -f2 | lines.humansize.sum
end
