# Defined interactively
function todo
    cat (echo $argv | psub) ~/j/private/todos.md | sponge ~/j/private/todos.md
end
