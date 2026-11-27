# Defined interactively
function lsar.remote --wraps='lsar'
    lsar (curl -s -r 0-500000 $argv | psub -s (path extension $argv))
end
