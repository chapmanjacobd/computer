# Defined interactively
function fzf.video
    fzf --preview-window="bottom:6:wrap" --preview="umpv --loop-file=inf --no-fullscreen {}"
end
