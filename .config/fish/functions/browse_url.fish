# Defined interactively
function browse_url
    library expand-links -s(fzf --multi < ~/.local/share/search_urls.list) $argv | open_browser.py
end
