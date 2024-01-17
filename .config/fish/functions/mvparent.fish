# Defined interactively
function mvparent --argument src dest
    lb relmv (path dirname "$src") "$dest"
end
