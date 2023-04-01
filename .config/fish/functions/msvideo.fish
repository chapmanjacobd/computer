# Defined via `source`
function msvideo
    rsync -a --remove-source-files --files-from=(                                   lb wt -u 'ntile(10000) over (order by size / duration) desc' -L 10 ~/lb/video.db $argv -p f --moved /mnt/d/ /mnt/d/70_Now_Watching/ | psub                                                                       ) /mnt/d/ /mnt/d/70_Now_Watching/
end
