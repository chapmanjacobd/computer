# Defined interactively
function watchfilehandles
    repeatslowly eval 'filehandles | coln 1 | sum_fish'
end
