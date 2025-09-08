# Defined interactively
function copying
    set -l exit_code 1

    if pgrep -fa torrents
        set exit_code 0
    end

    if pgrep -a mv
        set exit_code 0
    end

    if pgrep -fa 'lb mv'
        set exit_code 0
    end

    if pgrep -a rsync
        set exit_code 0
    end

    return $exit_code
end
