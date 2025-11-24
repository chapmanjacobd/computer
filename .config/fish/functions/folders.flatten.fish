# Defined interactively
function folders.flatten
    find . -type f -exec mv --backup=numbered -t (pwd) {} +
    remove_empty_directories
end
