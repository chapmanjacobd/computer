# Defined via `source`
function gitignore
    echo "$argv" | cat - .gitignore | sponge .gitignore
    git reset :/"$argv"
end
