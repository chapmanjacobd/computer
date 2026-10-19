# Defined interactively
function scandb --argument-names path
    lb db add fs --filesystem ~/disks/(path basename -- $path).fs.db $path
    lb db add fs --video ~/disks/(path basename -- $path).wt.db $path
    # lb db add fs --audio ~/disks/(path basename -- $path).lt.db $path
end
