# Defined interactively
function feed
    udisksctl status
    udisksctl mount -b /dev/sdi1
    rsync -ah --info=progress2 --no-inc-recursive --remove-sent-files /run/media/xk/LUMIX/DCIM/ ~/d/dump/projects/cinematograph/footage/
    udisksctl unmount -h -b /dev/sdi1
end
