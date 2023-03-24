# Defined interactively
function lt-dev
    ~/lb/
    python -m xklb.lb listen -w 'play_count=0' -k delete-if-audiobook audio.db $argv
end
