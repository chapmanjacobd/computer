# Defined interactively
function syncpcs
    ssh len clean_home
    print $servers | parallel sshpc {} git pull
    print $servers | parallel sshpc {} git -C lb/ pull
    print $servers | parallel sshpc {} pip install --upgrade lb/
end
