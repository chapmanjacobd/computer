# Defined interactively
function lt-dev
    ~/lb/
    python -m xklb.lb listen -k delete-if-audiobook audio.db $argv
end
