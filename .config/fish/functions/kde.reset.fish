# Defined interactively
function kde.reset
    ps.pause ffmpeg

    bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
    systemd-run --user kwin_x11 --replace
    systemctl --user restart pipewire-pulse.socket pipewire-pulse.service pipewire.service wireplumber.service

    sleep 3
    windows.maximize.all
    ps.resume.all
end
