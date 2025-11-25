# Defined interactively
function lb.test
    trash tests/data/*.db*
    pytest $argv
    and ruff check . --show-fixes
end
