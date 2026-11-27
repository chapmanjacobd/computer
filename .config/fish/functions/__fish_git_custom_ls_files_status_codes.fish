function __fish_git_custom_ls_files_status_codes --description 'List git ls-files -v status codes'
    printf '%s\t%s\n' \
        H Cached \
        S Skip-worktree \
        M Unmerged \
        R Removed \
        C Modified \
        K 'To be killed' \
        '?' Other
end
