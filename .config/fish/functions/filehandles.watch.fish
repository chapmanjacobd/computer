# Defined interactively
function file.handles.watch
    repeat.slowly eval 'file.handles | lines.coln 1 | lines.sum.fish'
end
