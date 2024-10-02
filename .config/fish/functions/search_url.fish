# Defined interactively
function search_url --description 'Expand a search URL'
    set -l search_url $argv[1]
    for query in $argv[2..-1]
        set -l encoded_query (string escape --style=url $query)
        echo (string replace "%s" $encoded_query $search_url)
    end
end
