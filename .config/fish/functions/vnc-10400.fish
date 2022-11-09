# Defined interactively
function vnc-10400
    ssh xk@10400 -f -L 4102:localhost:4000 sleep 20 && /usr/NX/bin/nxplayer --session ~/bin/nomachine/ssh_10400.nxs
end
