# Defined via `source`
function msvideo
    rsync -a --remove-source-files --files-from=(
        lb wt -u 'ntile(10000) over (order by size / duration) desc' -L 10 ~/lb/fs/video.db $argv -p f --moved /mnt/d/ ~/sync/video/other/ | psub
    ) /mnt/d/ ~/sync/video/other/
end
