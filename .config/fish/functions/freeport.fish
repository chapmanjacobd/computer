# Defined via `source`
function freeport
    if test (count $argv) -ne 1
        return 1
    end
    set -l current_port $argv[1]

    while test $current_port -le 65535
        set -l output (lsof -i tcp:$current_port -sTCP:LISTEN -n -P 2> /dev/null)

        if test -z "$output"
            echo $current_port
            return 0
        end

        set current_port (math $current_port + 1)
    end
    return 1
end
