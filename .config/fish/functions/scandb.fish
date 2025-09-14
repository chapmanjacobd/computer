# Defined interactively
function scandb --argument-names path
    lb fsadd --filesystem (path basename -- $path).db $path
    lb fsadd --video --audio (path basename -- $path).wt.db $path
end
