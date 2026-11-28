function monthly
    sudo btrfs filesystem defragment -r ~/lb/ ~/m/ ~/mc/ ~/j/
    forganize
    sudo btrfs filesystem defragment -r ~/lb/

    # sudo updatedb
    fish.history.vacuum ~/.local/share/fish/fish_history >> ~/.local/share/fish/big_history
    sudo btrfs filesystem defragment -r ~/.local/ ~/.config/ ~/.git/
end
