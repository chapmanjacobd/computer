# Defined interactively
function binaries
    argparse a/all -- $argv
    or return

    if set -q _flag_all
        # Lists all binary files tracked in the history
        git log --all --numstat | awk '/^-/ {print $3}' | sort -u
    else
        # Lists binary files in the current repository state
        git diff --numstat (git hash-object -t tree /dev/null) | awk '/^-/ {print $3}'
    end
end
