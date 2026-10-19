function git.files --description 'Print files added or modified in a commit or range'
    if test (count $argv) -eq 0
        echo 'Usage: git.files <commit|range>' >&2
        return 2
    end

    set -l root (git rev-parse --show-toplevel 2>/dev/null)
    if test $status -ne 0
        echo 'Not inside a git repository' >&2
        return 1
    end

    git -C $root diff --name-only --diff-filter=AM $argv
end
