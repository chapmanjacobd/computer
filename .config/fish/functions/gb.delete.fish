# Defined interactively
function gb.delete
    # List local branches NOT in a worktree, excluding current HEAD (*)
    set -l selections (git branch --format='%(if)%(worktreepath)%(then)%(else)%(refname:short)%(end)' | \
                    grep -v '^$' | \
                    grep -v "^\*" | \
                    fzf --multi \
                        --header "TAB to multi-select | ENTER to delete" \
                        --preview 'git log --oneline --graph --color=always -n 15 {}' \
                        --preview-window 'right:60%')

    for branch in $selections
        git branch -d "$branch"
    end
end
