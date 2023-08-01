function monthly
    sudo btrfs filesystem defragment -r ~/lb/ ~/m/ ~/mc/ ~/j/
    noswap fish -c forganize
    noswap fish -c fdupe
    sudo btrfs filesystem defragment -r ~/lb/ ~/m/ ~/mc/ ~/j/
end
