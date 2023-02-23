function getWikipediaText
    curl "https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&page=$argv" | jq '.parse.text[]' | html2text --ignore-links --images-to-alt --ignore-emphasis --no-automatic-links
end
