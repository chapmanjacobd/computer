# Defined interactively
function folders.flatten
    find . -type f -exec mv --backup=numbered -t (pwd) {} +
    folders.empty.delete
end
