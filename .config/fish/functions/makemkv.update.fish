# Defined interactively
function makemkv.update --argument v
    ~/.local/bin/
    trash makemkv*
    wget1 https://www.makemkv.com/download/makemkv-bin-$v.tar.gz
    wget1 https://www.makemkv.com/download/makemkv-oss-$v.tar.gz
    unardel.nodir makemkv*gz
    cd makemkv-oss*
    ./configure
    make
    sudo make install
    ../makemkv-bin*
    make
    sudo make install

    open https://forum.makemkv.com/forum/viewtopic.php?f=5&t=1053
end
