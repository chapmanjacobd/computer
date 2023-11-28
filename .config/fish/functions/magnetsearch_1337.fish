# Defined interactively
function magnetsearch_1337 --argument search
    for cat in TV Documentaries Movies XXX
        firefox --new-tab https://1337x.to/category-search/$search/$cat/1/
        read last_page_number
        lb links --file (lb links https://1337x.to/category-search/$search/$cat/(seq 1 $last_page_number)/ --path-include /torrent/ | psub) --path-include magnet: | ssh backup tee -a ~/.local/magnets
    end
end
