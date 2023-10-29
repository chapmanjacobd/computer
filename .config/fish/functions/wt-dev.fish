# Defined interactively
function wt-dev
    ~/lb/
    python -m xklb.lb watch --keep-dir /mnt/d/70_Now_Watching/keep/ -k delete video.db -v $argv
end
