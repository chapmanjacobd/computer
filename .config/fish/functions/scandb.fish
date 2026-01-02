# Defined interactively
function scandb --argument-names path
    lb fsadd --filesystem ~/disks/(path basename -- $path).fs.db $path
    lb fsadd --video --audio --delete-unplayable ~/disks/(path basename -- $path).wt.db $path
end
