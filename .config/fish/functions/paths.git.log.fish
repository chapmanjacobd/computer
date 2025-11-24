# Defined interactively
function paths.git.log
    for f in $argv
        git log --date=iso-strict-local --format="%ad %>(14) %cr %<(5) %an  %h ./$f" -- $f | sort --general-numeric-sort
    end
end
