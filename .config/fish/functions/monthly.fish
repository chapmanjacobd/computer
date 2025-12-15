function monthly
    sudo btrfs filesystem defragment -r ~/lb/ ~/m/ ~/mc/ ~/j/ ~/.git/
    forganize
    sudo btrfs filesystem defragment -r ~/lb/
    # sudo updatedb
end
