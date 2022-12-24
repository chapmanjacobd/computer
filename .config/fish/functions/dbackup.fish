# Defined via `source`
function dbackup --argument dfolder
    echo $dfolder
    rsync -ah --info=progress2 --no-inc-recursive --delete --delete-before /mnt/d/$dfolder/ backup:/mnt/d/$dfolder/
end
