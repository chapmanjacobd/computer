# Describe commands with cmd.info when interactive.
function type --description 'Describe a command (cmd.info for files)'
    if not status --is-interactive
        builtin type $argv
        return
    end
    if not set -q argv[1]
        builtin type $argv
        return
    end
    # cmd.info-only flags that builtin type does not understand.
    if contains -- $argv[1] --full --no-version --no-source --no-package --no-color --which --all --verbose
        cmd.info $argv
        return
    end
    if string match -qr '^-' -- $argv[1]
        builtin type $argv
        return
    end
    # Keep fish's native output for functions, builtins, keywords, and
    # missing names; only replace it when every argument is a file on PATH.
    for arg in $argv
        set -l kind (builtin type -t -- $arg 2>/dev/null)
        if test "$kind" != file
            builtin type $argv
            return
        end
    end
    cmd.info --which $argv
end
