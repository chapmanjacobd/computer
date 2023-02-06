# Defined interactively
function wt-dev
    ~/lb/
    python -m xklb.lb watch -u 'ntile(10000) over (order by size / duration) desc' -k delete video.db $argv
end
