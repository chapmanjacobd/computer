# Defined interactively
function git.maintenance.register
    if test (count $argv) -gt 0
        git -C $argv[1] maintenance register
    else
        git maintenance register
    end
end
