# Defined interactively
function git.path --description 'Print path relative to git repo root'
    if not git rev-parse --show-toplevel >/dev/null 2>&1
        echo "Not inside a git repository" >&2
        return 1
    end

    set root (git rev-parse --show-toplevel)

    if test (count $argv) -eq 0
        echo $root
        return 0
    end

    for arg in $argv
        # Resolve to absolute path
        if type -q realpath
            set abs (realpath $arg)
        else
            set abs (readlink -f $arg)
        end

        # Strip repo root prefix
        set rel (string replace -r "^$root/?" "" $abs)

        echo $rel
    end
end
