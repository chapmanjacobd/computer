# Defined interactively
function remount --wraps='mount'
    umount $argv
    mount $argv
end
