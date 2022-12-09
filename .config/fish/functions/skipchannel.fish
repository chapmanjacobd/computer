# Defined interactively
function skipchannel
    yt-dlp --flat-playlist --print "%(id)s" $argv | sed 's|.*|youtube \0|' >>~/.local/share/yt_archive.txt
end
