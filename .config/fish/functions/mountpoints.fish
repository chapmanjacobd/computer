# Defined interactively
function mountpoints
    mount | awk '{print $3}'
end
