# Defined interactively
function spongebob --argument dest
    # the unique sponge -- har har
    cat - $dest | awk '!seen[$0]++' | sponge $dest
end
