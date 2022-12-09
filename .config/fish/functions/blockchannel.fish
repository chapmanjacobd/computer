# Defined interactively
function blockchannel
    yt-dlp --flat-playlist --print "%(id)s" $argv | sed 's|.*|youtube \0|' >>~/.local/share/yt_archive.txt
end
