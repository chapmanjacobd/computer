# Defined interactively
function activate
    set PIPENV_ACTIVE haha
    cd $argv
    . $(pipenv --venv)/bin/activate.fish
end
