if not functions -q _worktree_ensure
    source $__fish_config_dir/functions/_worktree_helpers.fish
end

# zoxide jump with a git worktree fallback. `z project branch` still behaves
# like zoxide first, but when that lookup fails it resolves `project` and jumps
# to (or creates) the branch worktree instead of making you run several git
# commands.
function z --wraps=__zoxide_z --description 'zoxide jump, creating a missing worktree on a failed repo+branch lookup'
    set -l argc (builtin count $argv)

    if test $argc -ge 2
        and test "$argv[1]" != --
        and not string match -q -- '-*' $argv[1]

        # Query silently so a failed repo+branch lookup does not print
        # "zoxide: no match found" before the worktree fallback runs.
        set -l result (command zoxide query --exclude (__zoxide_pwd) -- $argv 2>/dev/null)
        if test $status -eq 0; and test -n "$result"
            __zoxide_cd $result
            return 0
        end

        set -l branch $argv[-1]
        set -l repo (_worktree_pick_repo $argv[1..-2])
        if test -z "$repo"
            # No repository matched. Delegate to zoxide for its normal error.
            __zoxide_z $argv
            return
        end

        # Preserve directory jumping for an existing but unindexed subdirectory
        # instead of creating a branch that happens to share its name.
        if test -d "$repo/$branch"
            __zoxide_cd "$repo/$branch"
            return 0
        end

        _worktree_ensure "$repo" "$branch"
        return
    end

    __zoxide_z $argv
end
