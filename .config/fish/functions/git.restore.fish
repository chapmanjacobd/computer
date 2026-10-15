# Defined interactively
function git.restore
    if test (count $argv) -gt 0
        git diff -- $argv
        git restore -- $argv
    else
        git diff
        git restore .
    end
end
