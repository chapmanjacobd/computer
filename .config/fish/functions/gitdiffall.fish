# Defined via `source`
function gitdiffall
    for branch in (git branch -r | grep -v HEAD | string trim)
        echo $branch
        git diff $branch $argv
    end
end
