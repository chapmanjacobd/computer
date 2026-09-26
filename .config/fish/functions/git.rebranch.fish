function git.rebranch --description "Rebase a branch flat onto the default branch, keeping only the stacks you select"
    set -l dry_run 0
    set -l branch (git rev-parse --abbrev-ref HEAD)

    for arg in $argv
        switch $arg
            case --dry-run
                set dry_run 1
            case '-*'
                echo "git.rebranch: unknown option: $arg" >&2
                return 2
            case '*'
                set branch $arg
        end
    end

    if not git rev-parse --verify --quiet "refs/heads/$branch" >/dev/null
        echo "git.rebranch: no such local branch: $branch" >&2
        return 1
    end

    # resolve the default branch (mirrors the `git main` alias)
    set -l main (git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | string replace -r '^refs/remotes/origin/' '')
    if test -z "$main"
        git remote set-head origin --auto >/dev/null 2>&1
        set main (git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | string replace -r '^refs/remotes/origin/' '')
    end
    if test -z "$main"
        set main main
    end

    # stacks = local branches that are ancestors of $branch, NOT reachable from $main,
    # excluding $branch and $main themselves
    set -l in_main (git branch --merged $main --format='%(refname:short)' 2>/dev/null)
    set -l stacks
    for b in (git branch --merged $branch --format='%(refname:short)' 2>/dev/null)
        if contains -- $b $in_main
            continue
        end
        if test "$b" = "$branch"; or test "$b" = "$main"
            continue
        end
        set -a stacks $b
    end

    if not set -q stacks[1]
        echo "no stacked branches: $branch is already on $main"
        return 0
    end

    # order bottom (closest to main) -> top (closest to $branch) by commits ahead of main
    set -l ordered
    for b in $stacks
        set -a ordered (printf '%s\t%s' (git rev-list --count $main..$b) $b)
    end
    set stacks (printf '%s\n' $ordered | sort -n | cut -f2-)

    set -l n (count $stacks)
    echo "$branch sits on $n stacked branch(es):"
    for b in $stacks
        printf '  %s  (%s ahead of %s)\n' $b (git rev-list --count $main..$b) $main
    end

    # ask which stacks to keep only when more than two branches are involved
    set -l keep
    if test $n -gt 2
        set keep (printf '%s\n' $stacks | fzf --multi \
            --header "Select stacks to KEEP on top of $main (Tab=toggle, Ctrl-A=all, Enter=drop all)" \
            --preview "git log --oneline --graph --no-decorate $main..{1} | head -30" \
            | string split '\n')
    else
        echo "fewer than 3 branches involved; flattening $branch onto $main (dropping all $n stack(s))"
    end

    # upstream for `git rebase --onto $main $upstream`: the branch just below the
    # deepest kept stack; nothing kept => drop everything (upstream = top stack)
    set -l upstream
    if set -q keep[1]
        set -l sel_idx 0
        for i in (seq (count $stacks))
            if contains -- $stacks[$i] $keep
                set sel_idx $i
                break
            end
        end
        if test $sel_idx -eq 0
            set upstream $stacks[-1]
        else if test $sel_idx -eq 1
            set upstream (git merge-base $main $stacks[1])
        else
            set upstream $stacks[(math $sel_idx - 1)]
        end
    else
        set upstream $stacks[-1]
    end

    echo
    echo "plan: git rebase --onto $main $upstream $branch"
    if test $dry_run -eq 1
        echo "(dry run; nothing executed)"
        return 0
    end

    read -P "proceed? [y/N] " -l answer
    if not string match -qi 'y*' -- $answer
        echo aborted
        return 1
    end

    git rebase --onto $main $upstream $branch
end
