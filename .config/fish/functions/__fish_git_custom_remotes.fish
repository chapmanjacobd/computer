function __fish_git_custom_remotes --description 'List remotes'
    git remote 2>/dev/null | while read -l remote
        printf '%s\t%s\n' $remote 'Remote'
    end
end
