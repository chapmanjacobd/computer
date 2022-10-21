# Defined interactively
function flattenDirectory
    find . -type f -exec mv --backup=numbered -t (pwd) {} +
    rmdir *
end
