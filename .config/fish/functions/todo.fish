# Defined interactively
function todo
    cat (echo $argv | psub) ~/j/private/todo.md | sponge ~/j/private/todo.md
end
