function __fish_git_custom_commits --description 'List recent commits on the current branch'
    git log --no-show-signature --pretty=tformat:'%h%x09%s' --max-count=50 2>/dev/null
end
