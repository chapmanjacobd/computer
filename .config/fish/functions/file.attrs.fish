# Defined interactively
function file.attrs --wraps='getfattr'
    getfattr -d -m ^ -R -- $argv
end
