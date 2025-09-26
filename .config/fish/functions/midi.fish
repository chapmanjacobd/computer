# Defined interactively
function midi
    timidity $argv -Ow -o - | ffplay -nodisp -autoexit -i -
end
