# Defined interactively
function git.ignore.local --description 'Add path(s) to .git/info/exclude'
    set root (git rev-parse --show-toplevel) ^/dev/null
    or begin
        echo "Not inside a git repository" >&2
        return 1
    end

    for rel in (git.path $argv)
        echo $rel >>$root/.git/info/exclude
    end
end
