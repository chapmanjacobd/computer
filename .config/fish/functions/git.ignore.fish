# Defined via `source`
function git.ignore --description 'Add path(s) to .gitignore'
    set root (git rev-parse --show-toplevel 2>/dev/null)
    or begin
        echo "Not inside a git repository" >&2
        return 1
    end

    for arg in $argv
        set rel (git.path $arg)
        echo /$rel >>$root/.gitignore

        echo git reset -- $root/$rel
        echo git rm --cached -- $root/$rel
    end
end
