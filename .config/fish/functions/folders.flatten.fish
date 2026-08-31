# Defined interactively
function folders.flatten
    find . -mindepth 2 -type f -exec mv --backup=numbered -t (pwd) {} +
    folders.empty.delete
end
