# Defined interactively
function ps.fzf.resume
    ps.resume (ps.paused | fzf.choose | cut -d' ' -f1)
end
