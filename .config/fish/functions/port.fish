function port
    sudo lsof +c 0 -i :$argv
end
