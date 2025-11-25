# Defined interactively
function lstrip --argument char
    sed "s|^$char||"
end
