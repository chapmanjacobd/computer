# Defined interactively
function torrent.size
    torrent_promote.py $argv -n 999999 -p | cut -d'#' -f2 | human_size_sum.py
end
