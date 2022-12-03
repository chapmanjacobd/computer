# Defined via `source`
function gitignore
    echo "$argv" | cat - .gitignore | sponge .gitignore
end
