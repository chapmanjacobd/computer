# Defined interactively
#
# Sync the current branch with <target>, preferring merge because it never
# rewrites history. A merge is cheaper to reason about, so it wins whenever it
# applies cleanly. Only when the merge conflicts do we test a rebase in a
# scratch worktree, and use the rebase if that applies cleanly. If both
# conflict, an incremental merge (git-imerge) breaks the resolution into
# pairwise conflicts; a plain merge is the fallback.
function git.merge.or.rebase --description 'Sync with a branch: merge if clean, otherwise rebase if that is clean'
    argparse --name='git merge-or-rebase' n/no-fetch h/help no-imerge -- $argv
    or return 2

    if set -q _flag_h
        echo 'Usage: git merge-or-rebase <target-branch> [--no-fetch] [--no-imerge]'
        echo
        echo 'Decides between merge and rebase for syncing the current branch with'
        echo '<target-branch> (for example iiab/master), then applies the winner.'
        echo
        echo '  - Merge wins whenever it applies cleanly (no history rewrite).'
        echo '  - If the merge conflicts, a rebase is tried in a scratch worktree.'
        echo '  - If both conflict, an incremental merge with git-imerge resolves'
        echo '    the conflicts one pair of commits at a time.'
        echo
        echo 'Options:'
        echo '  -n, --no-fetch   do not fetch <remote>/<branch> from its remote first'
        echo '      --no-imerge  if both conflict, run a plain merge instead of git-imerge'
        echo '  -h, --help       show this help'
        return 0
    end

    if test (count $argv) -ne 1
        echo >&2 'Usage: git merge-or-rebase <target-branch> [--no-fetch] [--no-imerge]'
        return 2
    end

    set -l target $argv[1]

    git rev-parse --is-inside-work-tree >/dev/null 2>&1
    or begin
        echo >&2 'git merge-or-rebase: not inside a git work tree'
        return 1
    end

    # Refresh a remote-tracking target such as iiab/master before resolving it.
    if not set -q _flag_n
        set -l parts (string split -m1 / -- $target)
        if test (count $parts) -eq 2
            and contains -- $parts[1] (git remote)
            echo "Fetching $parts[1] $parts[2]..."
            git fetch -- $parts[1] $parts[2]
            or begin
                echo >&2 "git merge-or-rebase: failed to fetch $parts[1] $parts[2]"
                return 1
            end
        end
    end

    set -l target_rev (git rev-parse --verify --quiet "$target^{commit}" 2>/dev/null)
    if test -z "$target_rev"
        echo >&2 "git merge-or-rebase: cannot resolve '$target' to a commit"
        return 1
    end

    if git merge-base --is-ancestor $target_rev HEAD
        echo "Already up to date: HEAD already contains $target."
        return 0
    end

    set -l dirty 0
    git diff --quiet; or set dirty 1
    git diff --cached --quiet; or set dirty 1
    if test $dirty = 1
        echo >&2 'git merge-or-rebase: working tree has uncommitted changes; commit or stash them first.'
        return 1
    end

    # Fast, object-level merge test. Exit status is non-zero on conflicts.
    if git merge-tree --write-tree HEAD $target_rev >/dev/null 2>&1
        echo "Merge applies cleanly onto $target; merging (history preserved)."
        git merge --ff --no-edit $target
        return $status
    end

    # The merge conflicts. Test the rebase in a throwaway worktree so the real
    # working tree and index stay untouched.
    echo "Merge conflicts; testing whether rebase applies cleanly..." >&2
    set -l scratch (mktemp -d /tmp/git-merge-or-rebase.XXXXXX)
    rmdir $scratch
    if not git worktree add --quiet --detach $scratch HEAD
        echo >&2 "git merge-or-rebase: could not create scratch worktree at $scratch"
        rm -rf $scratch
        return 1
    end

    set -l rebase_clean 0
    if git -C $scratch -c core.hooksPath=/dev/null rebase $target_rev >/dev/null 2>&1
        set rebase_clean 1
    else
        git -C $scratch rebase --abort >/dev/null 2>&1
    end
    git worktree remove --force $scratch >/dev/null 2>&1
    rm -rf $scratch
    git worktree prune >/dev/null 2>&1

    if test $rebase_clean = 1
        # Rebase rewrites history, so warn if these commits were published.
        set -l upstream (git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null)
        set -l published 0
        if test -n "$upstream"
            set -l upstream_rev (git rev-parse '@{upstream}' 2>/dev/null)
            if test -n "$upstream_rev"; and git merge-base --is-ancestor HEAD $upstream_rev
                set published 1
            end
        end

        echo "Merge conflicts, but rebase applies cleanly; rebasing onto $target."
        git rebase $target
        set -l rc $status
        if test $rc = 0; and test $published = 1
            echo "Note: these commits were already on '$upstream'; publish the rewritten history with:"
            echo "  git push --force-with-lease"
        end
        return $rc
    end

    # Neither path is conflict-free. An incremental merge presents one pairwise
    # conflict at a time and keeps the merge-shaped, history-preserving result.
    if not set -q _flag_no_imerge; and command -q git-imerge
        echo "Both merge and rebase conflict; starting an incremental merge onto $target." >&2

        # git-imerge names the merge after the target, which must be a valid
        # refname component. Fall back to a fixed name for commits/expressions.
        set -l imerge_args merge $target
        if not git check-ref-format "refs/imerge/$target" >/dev/null 2>&1
            set imerge_args merge --name=merge-or-rebase $target
        end

        git-imerge $imerge_args
        or begin
            echo >&2 'git-imerge could not start; rerun with --no-imerge to do a plain merge.'
            return 1
        end
        echo >&2 'Resolve conflicts one at a time, then run: git.continue'
        echo >&2 'The final git.continue finishes the incremental merge.'
        return 0
    end

    echo "Both merge and rebase conflict; running merge so conflicts can be resolved in place." >&2
    git merge --ff --no-edit $target
    set -l rc $status
    if test $rc != 0
        echo >&2 'Resolve the conflicts, then run: git.continue   (or git.abort to back out)'
    end
    return $rc
end
