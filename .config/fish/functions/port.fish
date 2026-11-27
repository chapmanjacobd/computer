function port --wraps='sudo'
    sudo lsof +c 0 -i :$argv
end
