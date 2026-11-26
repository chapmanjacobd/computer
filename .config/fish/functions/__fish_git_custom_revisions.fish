function __fish_git_custom_revisions --description 'List revisions usable as git arguments'
    printf '%s\t%s\n' HEAD 'HEAD'
    __fish_git_custom_refs
    __fish_git_custom_commits
end
