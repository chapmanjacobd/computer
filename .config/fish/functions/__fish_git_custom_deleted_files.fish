function __fish_git_custom_deleted_files --description 'List paths deleted in recent history'
    git log --all --max-count=1000 --diff-filter=D --name-only --pretty=format: 2>/dev/null \
        | string match -v '' \
        | sort -u
end
