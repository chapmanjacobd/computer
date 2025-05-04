# Defined interactively
function update_makemkv
    ~/bin/
    trash makemkv*
    wget https://www.makemkv.com/download/makemkv-bin-1.17.2.tar.gz
    wget https://www.makemkv.com/download/makemkv-oss-1.17.2.tar.gz
    unar makemkv*gz
    cd makemkv-oss*
    ./configure
    make
    sudo make install
    ../makemkv-bin*
    make
    sudo make install
end
