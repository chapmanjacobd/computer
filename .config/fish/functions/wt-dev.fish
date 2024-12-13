# Defined interactively
function wt-dev
    ~/lb/
    python -m library.lb watch --keep-dir /mnt/d/archive/video/other/ -k delete video.db --cmd5 'echo skip' -v $argv
end
