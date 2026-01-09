# Defined interactively
function scandb --argument-names path
    lb fsadd --filesystem ~/disks/(path basename -- $path).fs.db $path
    lb fsadd --video --delete-unplayable ~/disks/(path basename -- $path).wt.db $path
    # lb fsadd --audio --delete-unplayable ~/disks/(path basename -- $path).lt.db $path
end
