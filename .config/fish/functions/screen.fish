function screen --argument-names action
    switch $action
        case on
            kscreenctl on
        case off
            kscreenctl off
        case blank
            set -l idle 500
            if set -q argv[2]
                if test "$argv[2]" = no
                    set idle 99999
                else
                    set idle (math "max(1, $argv[2])" 2>/dev/null)
                    if test -z "$idle"
                        echo "usage: screen blank [no|<seconds>]" >&2
                        return 1
                    end
                end
            end
            # PowerDevil 6 reads display timeouts from powerdevilrc; the old
            # powermanagementprofilesrc file is only migration input now.
            kwriteconfig6 --file powerdevilrc --group AC --group Display --key TurnOffDisplayIdleTimeoutSec $idle
            qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement reparseConfiguration
        case virtual
            set -l preset $argv[2]
            set -l output $argv[3]
            if test -z "$preset" -o -z "$output"
                echo "usage: screen virtual <2880|laptop> <output>" >&2
                return 1
            end
            switch $preset
                case 2880
                    _screen.virtual_mode $output 423.75 2880 3104 3416 3952 1726 1729 1739 1789 -hsync +vsync
                case laptop
                    _screen.virtual_mode $output 165.25 1920 2040 2240 2560 1038 1041 1051 1077 -hsync +vsync
                case '*'
                    echo "screen: unknown virtual preset: $preset" >&2
                    return 1
            end
        case '*'
            echo "usage: screen on|off|blank [no|<seconds>]|virtual <2880|laptop> <output>" >&2
            return 1
    end
end
