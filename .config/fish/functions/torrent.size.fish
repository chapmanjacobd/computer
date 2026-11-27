# Defined interactively
function torrent.size --wraps='torrent.promote'
    torrent.promote $argv -n 999999 -p | cut -d'#' -f2 | lines.humansize.sum
end
