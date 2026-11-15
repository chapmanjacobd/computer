function screens --argument-names action
    switch $action
        case ''
            kscreenctl list-outputs --names
        case on
            kscreenctl on; or return 1
            bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
        case '*'
            echo "usage: screens [on]" >&2
            return 1
    end
end
