# Defined interactively
function zcat.web
    zcat (curl -s -r 0-500000 $argv | psub -s (path extension $argv))
end
