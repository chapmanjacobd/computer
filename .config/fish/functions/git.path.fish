# Defined interactively
function git.path --description 'Print path relative to git repo root'
    set root (git rev-parse --show-toplevel 2>/dev/null) || begin
        echo "Not inside a git repository" >&2
        return 1
    end

    if test (count $argv) -eq 0
        echo $root
        return
    end

    for arg in $argv
        set p $arg

        # If it doesn't exist, treat "/foo" as repo-root relative
        if not test -e $p
            if string match -q "/*" -- $p
                set p "$root/"(string trim -l -c / $p)
            end
        end

        set abs (path resolve $p)

        # Strip repo root prefix
        echo (string replace -r "^$root/?" "" -- $abs)
    end
end
