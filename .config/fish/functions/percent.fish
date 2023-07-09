# Defined interactively
function percent --argument num denum
    math -s1 "$num/$denum * 100"
end
