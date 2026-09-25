function git.rebranch.commits --description "fzf multi-select commits and cherry-pick them onto a new branch off main"
    set -l dry_run 0
    for arg in $argv
        switch $arg
            case --dry-run
                set dry_run 1
            case '-*'
                echo "git.rebranch.commits: unknown option: $arg" >&2
                return 2
        end
    end

    # safety: working tree must be clean before switching branches
    if not git diff --quiet; or not git diff --cached --quiet
        echo "working tree is dirty; commit or stash before rebranching" >&2
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

    # only the commits ahead of main on the current branch are candidates
    set -l log (git log --oneline --decorate $main..HEAD)
    if not set -q log[1]
        printf 'no commits ahead of %s on %s\n' $main (git rev-parse --abbrev-ref HEAD)
        return 0
    end

    set -l picked (printf '%s\n' $log | fzf --ansi --multi --no-sort --reverse --tiebreak=index \
        --header "Select commits to cherry-pick onto a new branch off $main (Tab=toggle, Ctrl-A=all, Enter=done)" \
        --preview 'git show --color=always (echo {} | cut -d" " -f1)' \
        --preview-window='right:60%:wrap' \
        | string split '\n' | string match -v '')

    if not set -q picked[1]
        echo "no commits selected"
        return 0
    end

    # extract shas (newest-first as shown), dedupe, then reverse for oldest-first cherry-pick
    set -l shas
    set -l seen
    for line in $picked
        set -l sha (echo $line | awk '{print $1}')
        if test -n "$sha"; and not contains -- $sha $seen
            set -a shas $sha
            set -a seen $sha
        end
    end
    set shas (printf '%s\n' $shas | tac | string match -v '')

    # default branch name from the newest selected commit's subject
    set -l newest $shas[-1]
    set -l def (git log -1 --format=%s $newest | string lower | string replace -ra '[^a-z0-9]+' '-' | string trim -c '-' | string sub -l 50)

    echo "selected $(count $shas) commit(s):"
    for sha in $shas
        echo "  $sha $(git log -1 --format=%s $sha)"
    end
    echo "new branch default: $def"
    read -P "branch name> " -l name
    if test -z "$name"
        set name $def
    end

    if git rev-parse --verify --quiet "refs/heads/$name" >/dev/null
        echo "branch already exists: $name" >&2
        return 1
    end

    echo
    echo "plan: git switch -c $name $main; and git cherry-pick $shas"
    if test $dry_run -eq 1
        echo "(dry run; nothing executed)"
        return 0
    end

    read -P "proceed? [y/N] " -l answer
    if not string match -qi 'y*' -- $answer
        echo "aborted"
        return 1
    end

    git switch -c $name $main
    and git cherry-pick $shas
end