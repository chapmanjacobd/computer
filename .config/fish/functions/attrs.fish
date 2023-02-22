# Defined interactively
function attrs
    getfattr -d -m ^ -R -- $argv
end
