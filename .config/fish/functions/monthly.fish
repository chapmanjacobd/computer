function monthly
    git gc --prune=now
    sudo btrfs filesystem defragment -r ~/lb/ ~/m/ ~/mc/ ~/j/ ~/.git/
    noswap fish -c forganize
    # noswap fish -c fdupe
    sudo btrfs filesystem defragment -r ~/lb/
end
