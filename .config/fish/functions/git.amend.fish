# Defined via `source`
function git.amend
    set tags (git tag --points-at HEAD)
    if test -n "$tags"
        if not confirm "Tags found pointing to HEAD: $tags. Continue? (y/N)"
            return 1
        end
    end

    git commit --amend --no-edit

    if test -n "$tags"
        for tag in $tags
            git tag -f "$tag" HEAD
        end
    end

    git push -f --force-with-lease --force-if-includes

    if test -n "$tags"
        git push -f --tags
    end
end
