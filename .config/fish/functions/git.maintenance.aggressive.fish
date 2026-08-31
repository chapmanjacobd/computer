# Defined interactively
function git.maintenance.aggressive
    if test (count $argv) -gt 0
        git -C $argv[1] maintenance run --task=gc --task=commit-graph --task=incremental-repack
    else
        git maintenance run --task=gc --task=commit-graph --task=incremental-repack
    end
end
