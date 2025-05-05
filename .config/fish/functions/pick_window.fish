# Defined interactively
function pick_window
    wmctrl -l -x | grep -v plasmashell.plasmashell | fzf | cut -f1 -d' '
end
