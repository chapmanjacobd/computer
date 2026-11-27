# Defined interactively
function lt.dev --wraps='python3'
    ~/lb/
    python -m library (lt.args) -v $argv
end
