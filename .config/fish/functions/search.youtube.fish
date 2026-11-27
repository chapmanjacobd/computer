# Defined interactively
function search.youtube --wraps='yt'
    yt --flat-playlist ytsearch20:"$argv" --print "%(url)s    %(title)s"
end
