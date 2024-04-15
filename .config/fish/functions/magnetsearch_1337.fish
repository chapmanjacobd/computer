# Defined interactively
function magnetsearch_1337 --argument search -a last_page_number
    lb links https://1337x.to/search/$search/(seq 1 $last_page_number)/ --path-include /torrent/ | lb links --path-include magnet: | ssh backup tee -a ~/.local/magnets
end
