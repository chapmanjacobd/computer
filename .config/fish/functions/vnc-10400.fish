# Defined interactively
function vnc-10400
    ssh xk@10400 -fN -L 4102:localhost:4000 && /usr/NX/bin/nxplayer --session ~/bin/nomachine/ssh_10400.nxs
end
