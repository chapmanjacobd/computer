# Defined interactively
function syncpcs
    print hk pakon backup r730xd len | parallel sshpc {} git pull
    print hk pakon backup r730xd len | parallel sshpc {} git -C lb/ pull
end
