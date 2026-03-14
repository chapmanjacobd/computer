# Defined interactively
function git.amend --argument-names target
    if test -n "$target"
        set commit $target
    else
        set commit (
            git log --oneline --decorate --color=always |
                fzf --ansi --no-sort --reverse --tiebreak=index \
                                    --prompt="fixup commit > " \
                                    --preview 'git show --color=always (echo {} | cut -d" " -f1)' |
                awk '{print $1}'
        )
    end

    if test -z "$commit"
        return
    end

    git commit --fixup=$commit
    # git push
end
