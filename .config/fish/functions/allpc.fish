# Defined interactively
function allpc
    parallel sshpc {} -- $argv ::: pakon backup len hk
end
