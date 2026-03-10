# Defined interactively
function gb.switch --argument-names query
    # Get local branches that are NOT active in any worktree
    # Filters out branches with a defined 'worktreepath'
    set -l selection (git branch --format='%(if)%(worktreepath)%(then)%(else)%(refname:short)%(end)' | \
                    grep -v '^$' | \
                    fzf --query "$query" --select-1 --exit-0 \
                        --header "Switch Local Branch (Idle Only)" \
                        --preview 'git log --oneline --graph --color=always -n 10 {}')

    if test -n "$selection"
        git switch "$selection"
    end
end
