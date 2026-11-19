function amedit --description 'Interactively edit the hunks in a commit (default: HEAD)'
    if test (count $argv) -eq 1
        if contains -- $argv[1] -h --help
            echo "usage: amedit [<commit>]"
            echo
            echo "Interactively choose which hunks of <commit> (default: HEAD) to keep."
            echo "The commit message is preserved. Unselected hunks are left as unstaged"
            echo "changes. When editing an older commit, unselected changes are stashed"
            echo "and restored after the rewritten history has been replayed. Binary"
            echo "changes cannot be hunk-selected and are kept automatically."
            return 0
        end
    end

    if test (count $argv) -gt 1
        echo "usage: amedit [<commit>]" >&2
        return 2
    end

    set -l commit HEAD
    if test (count $argv) -eq 1
        set commit $argv[1]
    end

    if not git rev-parse --is-inside-work-tree >/dev/null 2>&1
        echo "amedit: not inside a git work tree" >&2
        return 1
    end

    for marker in rebase-merge rebase-apply MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD
        if test -e (git rev-parse --git-path $marker)
            echo "amedit: another git operation is in progress ($marker)" >&2
            return 1
        end
    end

    git diff --quiet --ignore-submodules --
    set -l worktree_dirty $status
    git diff --cached --quiet --ignore-submodules --
    set -l index_dirty $status
    if test $worktree_dirty -ne 0 -o $index_dirty -ne 0
        echo "amedit: working tree and index must be clean" >&2
        return 1
    end

    set -l target (git rev-parse --verify --quiet "$commit^{commit}" 2>/dev/null)
    set -l target_status $status
    if test $target_status -ne 0
        echo "amedit: not a commit: $commit" >&2
        return 1
    end

    set -l head (git rev-parse HEAD)

    set -l parent (git rev-parse --verify --quiet "$target^" 2>/dev/null)
    set -l parent_status $status
    set -l is_root 0
    if test $parent_status -ne 0
        set is_root 1
        set parent (git hash-object -t tree /dev/null)
    end

    set -l parent_count (git rev-list --parents -n 1 $target | string split ' ' | count)
    if test $parent_count -gt 2
        echo "amedit: merge commits are not supported" >&2
        return 1
    end

    set -l rebasing 0
    if test "$target" != "$head"
        if not git merge-base --is-ancestor $target HEAD
            echo "amedit: $commit is not an ancestor of HEAD" >&2
            return 1
        end
        if not git rev-list --first-parent HEAD | string match -q -- $target
            echo "amedit: $commit is not on the first-parent history of HEAD" >&2
            return 1
        end
        set -l merges (git rev-list --min-parents=2 $target..HEAD)
        if test (count $merges) -gt 0
            echo "amedit: history between $commit and HEAD contains merge commits" >&2
            return 1
        end
        set rebasing 1
    end

    if test $rebasing -eq 1
        set -lx GIT_SEQUENCE_EDITOR "sed -i -e '0,/^pick /s/^pick /edit /'"
        if test $is_root -eq 1
            git -c rebase.abbreviateCommands=false rebase -i --root
        else
            git -c rebase.abbreviateCommands=false rebase -i $parent
        end
        set -l rebase_status $status
        set -e GIT_SEQUENCE_EDITOR
        if test $rebase_status -ne 0
            if test -e (git rev-parse --git-path rebase-merge)
                git rebase --abort
            end
            echo "amedit: could not start the rebase" >&2
            return 1
        end
    end

    set -l current (git rev-parse HEAD)
    if test "$current" != "$target"
        if test $rebasing -eq 1
            git rebase --abort
        end
        echo "amedit: rebase did not stop at the requested commit" >&2
        return 1
    end

    set -l tmpindex (mktemp)
    if test -z "$tmpindex"
        if test $rebasing -eq 1
            git rebase --abort
        end
        echo "amedit: could not create a temporary index" >&2
        return 1
    end
    rm -f $tmpindex
    set -lx GIT_INDEX_FILE $tmpindex
    if not git read-tree $parent
        set -e GIT_INDEX_FILE
        rm -f $tmpindex
        if test $rebasing -eq 1
            git rebase --abort
        end
        return 1
    end

    # Teach the temporary index about files the commit added, so add -p
    # can show their hunks instead of treating them as untracked.
    for path in (git diff --no-renames --name-only --diff-filter=A $parent $target)
        if not git add -N -f -- $path
            set -e GIT_INDEX_FILE
            rm -f $tmpindex
            if test $rebasing -eq 1
                git rebase --abort
            end
            echo "amedit: could not prepare $path for patching" >&2
            return 1
        end
    end

    # Binary changes have no hunks to select, so keep them in the commit
    # rather than silently dropping them.
    set -l binary_paths
    for line in (git diff --numstat --no-renames $parent $target)
        set -l fields (string split \t -- $line)
        if test (count $fields) -ge 3 -a "$fields[1]" = "-" -a "$fields[2]" = "-"
            set -a binary_paths $fields[3]
        end
    end
    if test (count $binary_paths) -gt 0
        echo "amedit: keeping binary changes (not hunk-selectable):" >&2
        for path in $binary_paths
            echo "  $path" >&2
        end
        if not git add -f -- $binary_paths
            set -e GIT_INDEX_FILE
            rm -f $tmpindex
            if test $rebasing -eq 1
                git rebase --abort
            end
            echo "amedit: could not stage binary changes" >&2
            return 1
        end
    end

    git add -p

    if git diff --cached --quiet $parent
        set -e GIT_INDEX_FILE
        rm -f $tmpindex
        if test $rebasing -eq 1
            git rebase --abort
        end
        echo "amedit: no hunks selected; commit unchanged"
        return 0
    end

    if not git commit --amend -C HEAD
        set -e GIT_INDEX_FILE
        rm -f $tmpindex
        if test $rebasing -eq 1
            git rebase --abort
        end
        echo "amedit: amend failed" >&2
        return 1
    end

    set -e GIT_INDEX_FILE
    rm -f $tmpindex
    git reset --quiet --mixed HEAD

    set -l newhead (git rev-parse HEAD)

    if test $rebasing -eq 0
        return 0
    end

    set -l affected (git diff --name-only $newhead $target)
    set -l stash_sha ""
    if test (count $affected) -gt 0
        set -l short_target (string sub -l 12 -- $target)
        set -l old_stash (git rev-parse --verify --quiet refs/stash)
        if not git stash push -u -m "amedit: unselected changes from $short_target" -- $affected
            echo "amedit: could not stash unselected changes" >&2
            echo "amedit: the rebase is still in progress; stash the changes and run 'git rebase --continue'" >&2
            return 1
        end
        set -l new_stash (git rev-parse --verify --quiet refs/stash)
        if test -n "$new_stash" -a "$new_stash" != "$old_stash"
            set stash_sha $new_stash
        end
    end

    set -l dirty (git status --porcelain --untracked-files=no)
    if test (count $dirty) -gt 0
        echo "amedit: uncommitted changes remain; rebase cannot continue" >&2
        echo "amedit: stash or commit them, then run 'git rebase --continue'" >&2
        if test -n "$stash_sha"
            echo "amedit: amedit's stash is $stash_sha" >&2
        end
        return 1
    end

    if not git rebase --continue
        echo "amedit: rebase stopped; resolve it and run 'git rebase --continue'" >&2
        if test -n "$stash_sha"
            echo "amedit: then restore unselected changes with: git stash apply $stash_sha" >&2
        end
        return 1
    end

    if test -n "$stash_sha"
        if not git stash apply $stash_sha
            echo "amedit: rebase finished, but the unselected changes did not apply cleanly" >&2
            echo "amedit: resolve the conflicts; the stash is still available as $stash_sha" >&2
            return 1
        end
        set -l current_stash (git rev-parse --verify --quiet refs/stash)
        if test "$current_stash" = "$stash_sha"
            git stash drop --quiet 'stash@{0}'
        else
            echo "amedit: applied stash $stash_sha (left in the stash list)" >&2
        end
    end

    return 0
end
