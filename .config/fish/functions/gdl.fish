# Defined interactively
function gdl
    ~/d/61_Photos_Unsorted/
    gallery-dl --no-check-certificate --download-archive $HOME/.local/share/gallerydl.sqlite3 $argv
end
