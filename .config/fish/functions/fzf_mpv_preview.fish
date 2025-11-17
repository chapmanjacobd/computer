# Defined interactively
function fzf_mpv_preview
    fzf --preview-window="bottom:6:wrap" --preview="umpv --loop-file=inf --no-fullscreen {}"
end
