# Shared helpers for z.fish and zg.fish. Config sources z.fish after zoxide
# init, and z.fish loads this file, so the helpers are normally always present.

# Print the main repository root for a directory, even when the directory is
# inside a linked worktree.
function _worktree_repo_root --argument-names dir
    set -l common (git -C "$dir" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
    or return 1

    if test (basename "$common") = .git
        dirname "$common"
    else
        echo "$common"
    end
end

# Print "branch<TAB>path" for every attached worktree.
function _worktree_list --argument-names repo
    set -l path ''
    set -l branch ''

    for line in (git -C "$repo" worktree list --porcelain 2>/dev/null)
        if string match -q 'worktree *' -- $line
            set path (string replace -r '^worktree ' '' -- $line)
        else if string match -q 'branch refs/heads/*' -- $line
            set branch (string replace -r '^branch refs/heads/' '' -- $line)
        else if test -z "$line"
            if test -n "$path"; and test -n "$branch"
                printf '%s\t%s\n' $branch $path
            end
            set path ''
            set branch ''
        end
    end

    if test -n "$path"; and test -n "$branch"
        printf '%s\t%s\n' $branch $path
    end
end

# Print "branch<TAB>kind<TAB>detail" rows for fzf. Worktrees come first, then
# local branches, then remote-tracking branches whose local branch is missing.
function _worktree_branch_rows --argument-names repo
    set -l seen

    for row in (_worktree_list "$repo")
        set -l parts (string split \t -- $row)
        printf '%s\tworktree\t%s\n' $parts[1] $parts[2]
        set -a seen $parts[1]
    end

    for branch in (git -C "$repo" for-each-ref --sort=-committerdate --format='%(refname:short)' refs/heads/ 2>/dev/null)
        if not contains -- $branch $seen
            printf '%s\tlocal\t%s\n' $branch ''
            set -a seen $branch
        end
    end

    for full_ref in (git -C "$repo" for-each-ref --sort=-committerdate --format='%(refname)' refs/remotes/ 2>/dev/null)
        set -l ref (string replace -r '^refs/remotes/' '' -- $full_ref)
        if string match -q '*/HEAD' -- $ref
            continue
        end

        set -l short (string replace -r '^[^/]+/' '' -- $ref)
        if not contains -- $short $seen
            printf '%s\tremote\t%s\n' $ref $short
            set -a seen $short
        end
    end
end

# Resolve a zoxide query to a unique git repository root.
function _worktree_pick_repo --argument-names query
    if test (count $query) -eq 1; and test -d "$query[1]"
        _worktree_repo_root "$query[1]"
        return
    end

    # Split quoted queries back into zoxide keywords. Whole-path queries were
    # handled above, so this only affects multi-word repository searches.
    set -l keywords
    for word in $query
        set -a keywords (string split -n ' ' -- $word)
    end

    set -l dirs
    if test (count $keywords) -gt 0
        set -a dirs (command zoxide query --list -- $keywords 2>/dev/null | head -n 200)
    else
        set -a dirs (command zoxide query --list 2>/dev/null | head -n 200)
    end

    set -l roots
    for dir in $dirs
        test -d "$dir"; or continue

        set -l root (_worktree_repo_root "$dir")
        if test -n "$root"; and not contains -- $root $roots
            set -a roots $root
        end
    end

    if test (count $roots) -eq 0
        return 1
    else if test (count $roots) -eq 1
        printf '%s\n' $roots[1]
        return 0
    end

    set -l selection (printf '%s\n' $roots | fzf \
        --select-1 \
        --exit-0 \
        --header 'Select repository' \
        --preview 'git -C {} status -sb; echo "---"; git -C {} worktree list' \
        --preview-window 'right:60%')

    test -n "$selection"; or return 1
    printf '%s\n' $selection
end

# Pick a branch, or accept a typed branch name as a new branch.
function _worktree_pick_branch --argument-names repo query
    set -l rows (_worktree_branch_rows "$repo")
    if test (count $rows) -eq 0
        return 1
    end

    set -lx ZW_REPO $repo
    set -l out (printf '%s\n' $rows | fzf \
        --delimiter=\t \
        --nth=1 \
        --with-nth=1,2 \
        --query "$query" \
        --print-query \
        --select-1 \
        --exit-0 \
        --header "Branch in "(basename "$repo")" | type a new branch name to create it" \
        --preview 'git -C "$ZW_REPO" log --oneline --graph --decorate --color=always -n 15 {1}; if [ {2} = worktree ]; then printf "\n--- worktree ---\n"; git -C {3} status -sb; fi' \
        --preview-window 'right:60%')
    set -l fzf_status $status

    # fzf returns 1 when Enter is pressed with no matching row; that is how a
    # typed new branch arrives. Esc and real failures must not create anything.
    if test $fzf_status -ne 0; and test $fzf_status -ne 1
        return 1
    end

    set -l lines (string split \n -- $out)
    set -l typed $lines[1]
    set -l chosen $lines[2]

    if test -n "$chosen"
        set -l parts (string split \t -- $chosen)
        printf '%s\n' $parts[1]
        return 0
    end

    if test -n "$typed"
        printf '%s\n' $typed
        return 0
    end

    return 1
end

# Find the origin default branch, preferring it over the local default.
function _worktree_default_branch --argument-names repo
    set -l ref (git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
    if test -n "$ref"
        string replace -r '^origin/' '' -- $ref
        return 0
    end

    for candidate in main master
        if git -C "$repo" show-ref --verify --quiet refs/remotes/origin/$candidate
            echo $candidate
            return 0
        end
    end

    for candidate in main master
        if git -C "$repo" show-ref --verify --quiet refs/heads/$candidate
            echo $candidate
            return 0
        end
    end

    set -l init (git -C "$repo" config --get init.defaultBranch 2>/dev/null)
    if test -n "$init"; and git -C "$repo" show-ref --verify --quiet refs/heads/$init
        echo $init
        return 0
    end

    set -l current (git -C "$repo" symbolic-ref --quiet --short HEAD 2>/dev/null)
    if test -n "$current"
        echo $current
        return 0
    end

    return 1
end

# Jump to the branch worktree, creating it when necessary.
function _worktree_ensure --argument-names repo branch
    set -l local_branch $branch
    set -l remote_ref ''

    if not git -C "$repo" show-ref --verify --quiet refs/heads/$branch
        if string match -q '*/*' -- $branch; and git -C "$repo" show-ref --verify --quiet refs/remotes/$branch
            set remote_ref $branch
            set local_branch (string replace -r '^[^/]+/' '' -- $branch)
        else
            for full_ref in (git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/ 2>/dev/null)
                set -l ref (string replace -r '^refs/remotes/' '' -- $full_ref)
                if string match -q '*/HEAD' -- $ref
                    continue
                end

                set -l short (string replace -r '^[^/]+/' '' -- $ref)
                if test "$short" = "$branch"
                    set remote_ref $ref
                    set local_branch $branch
                    break
                end
            end
        end
    end

    if not git -C "$repo" check-ref-format --branch "$local_branch" >/dev/null 2>&1
        echo "worktree: invalid branch name: $local_branch" >&2
        return 2
    end

    # The branch may already be checked out in any worktree, including the main
    # checkout. This also handles a branch passed as "origin/name".
    for row in (_worktree_list "$repo")
        set -l parts (string split \t -- $row)
        if test "$parts[1]" = "$local_branch"
            command zoxide add -- $parts[2] 2>/dev/null
            cd $parts[2]
            return 0
        end
    end

    set -l wt_path "$HOME/.git-worktrees/"(basename "$repo")"/$local_branch"
    if test -e "$wt_path"
        echo "worktree: path already exists but is not registered: $wt_path" >&2
        return 1
    end
    mkdir -p (dirname "$wt_path")

    set -l add_status
    if git -C "$repo" show-ref --verify --quiet refs/heads/$local_branch
        git -C "$repo" worktree add -q -- $wt_path $local_branch
        set add_status $status
    else if test -n "$remote_ref"
        git -C "$repo" worktree add -q --track -b $local_branch -- $wt_path $remote_ref
        set add_status $status
    else
        if git -C "$repo" remote get-url origin >/dev/null 2>&1
            printf 'worktree: fetching origin...\n' >&2
            git -C "$repo" fetch -q --prune origin
            or printf 'worktree: fetch failed; using existing refs\n' >&2
        end

        set -l default (_worktree_default_branch "$repo")
        set -l base HEAD
        if test -n "$default"
            if git -C "$repo" show-ref --verify --quiet refs/remotes/origin/$default
                set base origin/$default
            else if git -C "$repo" show-ref --verify --quiet refs/heads/$default
                set base $default
            end
        end

        git -C "$repo" worktree add -q -b $local_branch -- $wt_path $base
        set add_status $status
    end

    if test $add_status -ne 0
        echo "worktree: failed to create worktree" >&2
        return $add_status
    end

    command zoxide add -- $wt_path 2>/dev/null
    printf 'worktree: created %s\n' $wt_path >&2
    cd $wt_path
end
