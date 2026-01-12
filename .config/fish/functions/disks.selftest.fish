# Defined via `source`
function disks.selftest
    for drive in $argv
        sudo smartctl -a $drive | grep -E "Power_On_Hours|Power On Hours|Self-test execution status"
        echo
        sudo smartctl -l selftest $drive
        echo

        read -l -P "Run long self-test on $drive? [y/N] " confirm
        if test "$confirm" = y -o "$confirm" = Y
            sudo smartctl -t long $drive
        end
        echo
        echo
    end
end
