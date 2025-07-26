function monthly
    sudo journalctl --vacuum-time=10d

    git gc --prune=now
    sudo btrfs filesystem defragment -r ~/lb/ ~/m/ ~/mc/ ~/j/ ~/.git/
    forganize
    sudo btrfs filesystem defragment -r ~/lb/
    # sudo updatedb
end
