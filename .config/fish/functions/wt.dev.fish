# Defined interactively
function wt.dev --wraps='python3'
    ~/lb/
    python -m library play video --cmd5 'echo skip' -v $argv
end
