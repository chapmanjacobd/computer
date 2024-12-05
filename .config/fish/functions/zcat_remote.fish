# Defined interactively
function zcat_remote
    zcat (curl -s -r 0-500000 $argv | psub -s (path extension $argv))
end
