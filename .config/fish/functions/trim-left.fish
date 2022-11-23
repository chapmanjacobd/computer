# Defined interactively
function trim-left --argument char
    sed "s|^$char||"
end
