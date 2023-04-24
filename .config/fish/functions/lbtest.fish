# Defined interactively
function lbtest
    trash-put tests/data/*.db*
    pytest $argv
    and ruff check . --show-source
end
