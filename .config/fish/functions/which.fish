# Locate executables with cmd.info so PATH matches include file metadata.
function which --description 'Locate an executable with cmd.info'
    if not status --is-interactive
        command which $argv
        return
    end
    if not set -q argv[1]
        command which $argv
        return
    end
    if contains -- $argv[1] --version -v -V
        command which $argv
        return
    end
    cmd.info --which $argv
end
