# Defined interactively
function scandb --argument-names path
    lb fsadd --filesystem ~/disks/(path basename -- $path).db $path
    lb fsadd --video --audio ~/disks/(path basename -- $path).wt.db $path
end
