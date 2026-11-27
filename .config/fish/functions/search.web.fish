# Defined interactively
function search.web --wraps='library'
    library text expand links -s(fzf --multi < ~/.local/share/search_urls.list) "$argv" | open.browser
end
