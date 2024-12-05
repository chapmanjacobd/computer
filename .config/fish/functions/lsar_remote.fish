# Defined interactively
function lsar_remote
    lsar (curl -s -r 0-500000 $argv | psub -s (path extension $argv))
end
