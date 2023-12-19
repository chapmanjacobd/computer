# Defined interactively
function ytsearch
    yt --flat-playlist ytsearch20:"$argv" --print "%(url)s    %(title)s"
end
