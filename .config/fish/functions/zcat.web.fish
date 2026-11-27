# Defined interactively
function zcat.web --wraps='zcat'
    zcat (curl -s -r 0-500000 $argv | psub -s (path extension $argv))
end
