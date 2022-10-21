# Defined interactively
function restartplasma
    bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
    kwin_x11 --replace & disown
end
