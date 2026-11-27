# Defined interactively
function midi --wraps='timidity'
    timidity $argv -Ow -o - | ffplay -nodisp -autoexit -i -
end
