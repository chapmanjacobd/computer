# Defined interactively
function torrent.count
    torrent.promote $argv -n 999999 --count -p | cut -d'#' -f2 | lines.sum
end
