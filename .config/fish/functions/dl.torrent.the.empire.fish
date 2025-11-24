# Defined interactively
function dl.torrent.the.empire
    load.env.the.empire

    for url in $argv
        if not grep -i $url ~/.local/data/qbittorrent/the_empire_click.urls >/dev/null
            echo $url
            curl_retry.py --move ~/.local/data/qbittorrent/the_empire_click/ --filetype bittorrent "curl -OJs -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0' -H 'Referer: https://theempire.click/details.php' -H 'Cookie: $THE_EMPIRE_COOKIE'" $url
            sleep 8m
            echo $url >>~/.local/data/qbittorrent/the_empire_click.urls
        end
    end
end
