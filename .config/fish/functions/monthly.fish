function monthly
    noswap fish -c fdupe
    noswap fish -c forganize
    sudo btrfs filesystem defragment -r ~/lb/ ~/m/ ~/mc/ ~/j/
end
