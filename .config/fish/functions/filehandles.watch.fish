# Defined interactively
function filehandles.watch
    repeatslowly eval 'filehandles | coln 1 | lines.sum.fish'
end
