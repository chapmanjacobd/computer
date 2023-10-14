# Defined via `source`
function gitignore
    echo "$argv" | cat - .gitignore | sponge .gitignore
    git reset -- :/"$argv"
    if gum confirm --default=no
        git rm --cached "$argv"
        git commit -m wip
    end
end
