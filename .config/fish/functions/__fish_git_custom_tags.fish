function __fish_git_custom_tags --description 'List tags'
    git tag --list 2>/dev/null | while read -l tag
        printf '%s\t%s\n' $tag 'Tag'
    end
end
