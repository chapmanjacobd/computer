# Defined interactively
function filehandles.watch
    repeatslowly eval 'filehandles | lines.coln 1 | lines.sum.fish'
end
