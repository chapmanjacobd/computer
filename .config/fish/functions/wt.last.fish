# Defined interactively
function wt.last
    lb wt ~/lb/video.db -p v --cols path,duration,time_partial_first,time_partial_last -w time_deleted'>'-1 -l 10 $argv
end
