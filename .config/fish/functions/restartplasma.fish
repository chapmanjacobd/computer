# Defined interactively
function restartplasma
    bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
    systemd-run --user kwin_x11 --replace
end
