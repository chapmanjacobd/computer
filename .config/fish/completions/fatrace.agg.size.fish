complete -c fatrace.agg.size -f
complete -c fatrace.agg.size -l sort -x -a 'time_created time_created:desc time_modified time_modified:desc size size:desc' -d 'Sort mode'
complete -c fatrace.agg.size -s E -l exclude -x -d 'Exclude paths containing this substring'
complete -c fatrace.agg.size -l min-size -x -d 'Exclude files smaller than this'
complete -c fatrace.agg.size -l min-delta -x -d 'Exclude size deltas smaller than this'
