# Defined interactively
function lbtest
    trash-put tests/data/*.db*
    pytest $argv
    and pylint **/*.py
end
