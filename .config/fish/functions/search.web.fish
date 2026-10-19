# Defined interactively
function search.web
    library text expand links -s(fzf --multi < ~/.local/share/search_urls.list) "$argv" | open.browser
end
