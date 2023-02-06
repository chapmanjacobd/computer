# Defined interactively
function lt-dev
    ~/lb/
    python -m xklb.lb listen audio.db -k delete-if-audiobook $argv
end
