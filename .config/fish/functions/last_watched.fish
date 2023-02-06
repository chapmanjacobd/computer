# Defined interactively
function last_watched
    lb wt video.db -p v --cols path,duration,time_partial_first,time_partial_last
end
