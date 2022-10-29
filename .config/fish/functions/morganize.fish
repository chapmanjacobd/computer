function morganize
    for f in ~/m/tabs*.txt
        sort --unique --stable --ignore-case --random-sort $f | sponge $f
    end
    for f in ~/.config/fish/functions/*.fish
        fish_indent -w $f
    end

    for f in ~/mc/*.txt
        sort --unique --stable --ignore-case $f | sed '/^$/d' | sponge $f
    end

end
