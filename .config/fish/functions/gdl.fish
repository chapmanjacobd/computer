# Defined interactively
function gdl
    ~/d/61_Photos_Unsorted/
    gallery-dl --filter "extension in ('jpg', 'jpeg', 'webp')" --download-archive $HOME/.local/share/gallerydl.sqlite3 $argv
end
