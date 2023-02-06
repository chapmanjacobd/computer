# Defined interactively
function wt-dev
    ~/lb/
    python -m xklb.lb watch video.db -u 'ntile(10000) over (order by size / duration) desc' -k delete $argv
end
