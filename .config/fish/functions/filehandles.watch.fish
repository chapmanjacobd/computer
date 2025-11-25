# Defined interactively
function file.handles.watch
    repeatslowly eval 'file.handles | lines.coln 1 | lines.sum.fish'
end
