# Defined via `source`
function javtiful_search --argument query total
    javtiful_links 'search/sort=newest/videos?search_query='$query $total
end
