# Defined interactively
function standup.horizontal
    _screen.only 'DVI-D-[0-9]+' 1920x1080@60
    or return 1

    # ultrawideMonocle.off
    #bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
    screen blank && xset +dpms
    #breaktimer disable
    session.reset &
end
