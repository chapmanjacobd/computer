# Defined interactively
function the_empire_dl
    load_env_the_empire

    for url in (cb)
        if not grep -i $url ~/.local/data/qbittorrent/the_empire_click.urls >/dev/null
            echo $url
            curl_retry.py --move ~/.local/data/qbittorrent/the_empire_click/ --filetype bittorrent "curl -OJs -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0' -H 'Referer: https://theempire.click/details.php' -H 'Cookie: $THE_EMPIRE_COOKIE'" $url
            sleep (minutes 8)
            echo $url >>~/.local/data/qbittorrent/the_empire_click.urls
        end
    end
end
