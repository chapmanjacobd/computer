# Defined interactively
function _exec_with_prefix
    if not set -q COMMAND_PREFIX; or test -z "$COMMAND_PREFIX"
        commandline -f execute
        return
    end

    set cmd (commandline)

    if test -z "$cmd"
        commandline -f execute
        return
    end
    if string match -q 'commandline*' "$cmd"
        commandline -f execute
        return
    end

    history append $cmd
    echo
    eval $COMMAND_PREFIX $cmd
    commandline ''
    commandline -f repaint
end
