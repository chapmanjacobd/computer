function __fish_git_custom_local_branches --description 'List local branches'
    git for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null | while read -l branch
        printf '%s\t%s\n' $branch 'Local branch'
    end
end
