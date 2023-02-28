# Defined interactively
function restartplasma
    bash -c 'kquitapp5 plasmashell || killall plasmashell; systemd-run --user kstart5 plasmashell'
    systemd-run --user kwin_x11 --replace
end
