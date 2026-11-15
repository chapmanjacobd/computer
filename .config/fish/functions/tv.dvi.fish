# Defined interactively
function tv.dvi
    _screen.only 'DVI-D-[0-9]+' 1920x1080@60
    or return 1
    bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
end
