# Defined interactively
function wt-dev
    ~/lb/
    python -m xklb.lb watch -k delete -u 'ntile(10000) over (order by size / duration) desc' $argv
end
