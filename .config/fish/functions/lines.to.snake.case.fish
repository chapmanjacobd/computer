# Defined via `source`
function lines.to.snake.case
    sed -E 's/[^A-Za-z0-9_\n]+/_/g' | sed -E 's/__+/_/g' | tr '[:upper:]' '[:lower:]'
end
