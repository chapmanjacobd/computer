# Defined in /tmp/fish.Vi26bD/watchvideos.fish @ line 2
function watchvideos
    while mpvonce (files | fileTypeVideos | head -1) $argv; and :
    end
end
