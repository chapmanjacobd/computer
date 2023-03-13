# Defined via `source`
function msvideo
    rsync -a --remove-source-files --files-from=(                                   wt ~/lb/video.db -L 10 $argv -p f --moved /mnt/d/ /mnt/d/70_Now_Watching/ | psub                                                                       ) /mnt/d/ /mnt/d/70_Now_Watching/
end
