function git.select.commit
    set -l prompt_text "select commit > "
    if test (count $argv) -gt 0
        set prompt_text $argv[1]
    end

    git log --oneline --decorate --color=always --invert-grep --grep='^fixup! ' --grep='^squash! ' --grep='^amend! ' |
        fzf --ansi --no-sort --reverse --tiebreak=index \
            --prompt="$prompt_text" \
            --preview 'git show --color=always (echo {} | cut -d" " -f1)' |
        awk '{print $1}'
end
