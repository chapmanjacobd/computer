# Defined interactively
function scandb --argument-names path
    lb-dev fsadd --filesystem ~/(path basename -- $path).db $path
    lb-dev fsadd --video --audio ~/(path basename -- $path).wt.db $path
end
