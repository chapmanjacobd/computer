# Defined interactively
function torrent_count
    torrent_promote.py $argv -n 999999 --count -p | cut -d'#' -f2 | lines.sum
end
