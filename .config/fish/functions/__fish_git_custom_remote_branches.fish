function __fish_git_custom_remote_branches --description 'List remote-tracking branches'
    git for-each-ref --format='%(refname:short)' refs/remotes 2>/dev/null \
        | string match -v '*/HEAD' \
        | while read -l branch
            printf '%s\t%s\n' $branch 'Remote branch'
        end
end
