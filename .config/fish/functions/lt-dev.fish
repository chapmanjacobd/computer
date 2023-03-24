# Defined interactively
function lt-dev
    ~/lb/
    python -m xklb.lb listen -w 'play_count=0' -k delete-if-audiobook -v audio.db $argv
end
