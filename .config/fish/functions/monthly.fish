function monthly
    git gc --prune=now
    sudo btrfs filesystem defragment -r ~/lb/ ~/m/ ~/mc/ ~/j/ ~/.git/
    forganize
    sudo btrfs filesystem defragment -r ~/lb/
end
