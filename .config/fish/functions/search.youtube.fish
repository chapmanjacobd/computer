# Defined interactively
function search.youtube
    yt --flat-playlist ytsearch20:"$argv" --print "%(url)s    %(title)s"
end
