# Rename the current branch using the repository's branch-name convention.
function git.rename
    if test (count $argv) -eq 0
        printf '%s\n' 'usage: git rename <name> [words...]' >&2
        return 2
    end

    # Preserve the original git branch -M old new form.
    if test (count $argv) -eq 2; and command git show-ref --verify --quiet "refs/heads/$argv[1]"
        command git branch -M $argv
        return $status
    end

    command git branch -M (branchname $argv)
end
