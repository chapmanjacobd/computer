# Defined interactively
function spongebob --argument dest
    # the unique sponge -- har har
    cat - $dest | sponge $dest
end
