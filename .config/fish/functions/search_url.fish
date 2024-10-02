# Defined via `source`
function search_url --description 'Expand a search URL'
    set -l search_url $argv[1]

    for query in $argv[2..-1]
        # Replace unwanted characters with an empty string
        set -l cleaned_query (string replace -ra '[()\[\]'"',]+" '' $query)
        set -l encoded_query (string escape --style=url $cleaned_query)
        echo (string replace "%s" $encoded_query $search_url)
    end
end
