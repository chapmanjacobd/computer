# Defined interactively
function allpc
    parallel -j0 sshpc {} -- $argv ::: pakon backup len hk
end
