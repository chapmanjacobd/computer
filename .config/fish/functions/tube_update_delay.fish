# Defined interactively
function tube_update_delay
    sqlite-utils $argv -t 'select extractor_key, count(*) as count, hours_update_delay from playlists group by 1,3 order by extractor_key,count desc'
end
