# Defined interactively
function allpc
    parallel -j0 sshpc {} -- $argv ::: $servers
end
