# Defined interactively
function remount
    umount $argv
    mount $argv
end
