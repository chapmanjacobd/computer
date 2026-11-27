# Defined interactively
function todo --wraps='cat'
    cat (echo $argv | psub) ~/j/private/todo.md | sponge ~/j/private/todo.md
end
