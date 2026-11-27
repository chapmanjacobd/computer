# Defined interactively
function torrent.count --wraps='torrent.promote'
    torrent.promote $argv -n 999999 --count -p | cut -d'#' -f2 | lines.sum
end
