# Defined interactively
function pchildren --wraps=pgrep
    if test (count (string match -r '^[0-9]+$' -- $argv)) -eq (count $argv)
        set pids $argv
    else
        set pids (pgrep -n $argv)
    end

    pstree -lap $pids
end
