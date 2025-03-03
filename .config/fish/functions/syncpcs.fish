# Defined interactively
function syncpcs
    echon hk pakon backup r730xd len | parallel sshpc {} git pull
    echon hk pakon backup r730xd len | parallel sshpc {} git -C lb/ pull
end
