# Defined interactively
function gdl
    ~/d/dump/porn/image/
    gallery-dl --filter "extension in ('jpg', 'jpeg', 'webp')" --download-archive $HOME/.local/share/gallerydl.sqlite3 $argv
end
