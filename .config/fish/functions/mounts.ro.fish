# Defined interactively
function mounts.ro
    mount | grep -vE '/run/credentials|/sysroot' | grep -i ro,
end
