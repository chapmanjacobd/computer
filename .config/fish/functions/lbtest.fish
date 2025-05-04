# Defined interactively
function lbtest
    trash tests/data/*.db*
    pytest $argv
    and ruff check . --show-fixes
end
