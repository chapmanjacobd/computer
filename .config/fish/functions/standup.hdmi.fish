# Defined interactively
function standup.hdmi
    _screen.only 'HDMI(-A)?-[0-9]+' 1920x1080@60 270
    or return 1
    bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
end
