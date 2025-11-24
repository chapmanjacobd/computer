# Defined interactively
function windows.fzf
    wmctrl -l -x | grep -v plasmashell.plasmashell | fzf | cut -f1 -d' '
end
