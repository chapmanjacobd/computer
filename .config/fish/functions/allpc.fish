# Defined interactively
function allpc
    parallel -j0 sshpc {} -- $argv ::: pakon backup r730xd len hk
end
