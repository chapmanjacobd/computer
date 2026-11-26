function __fish_git_custom_status_codes --description 'List git status porcelain status codes'
    printf '%s\t%s\n' \
        M 'Modified' \
        T 'Type changed' \
        A 'Added' \
        D 'Deleted' \
        R 'Renamed' \
        C 'Copied' \
        U 'Unmerged' \
        '?' 'Untracked' \
        '!' 'Ignored'
end
