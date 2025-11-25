# Defined interactively
function file.attrs
    getfattr -d -m ^ -R -- $argv
end
