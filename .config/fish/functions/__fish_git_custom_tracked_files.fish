function __fish_git_custom_tracked_files --description 'List files tracked by git'
    git ls-files 2>/dev/null
end
