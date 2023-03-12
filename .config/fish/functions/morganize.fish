# Defined in /home/xk/.config/fish/functions/morganize.fish @ line 1
function morganize
    for f in ~/.config/fish/functions/*.fish
        fish_indent -w $f
    end

    for f in ~/mc/*.txt
        sort --unique --stable --ignore-case $f | sed '/^$/d' | sponge $f
    end

    for f in ~/mc/tabs.txt
        sort --unique --stable --ignore-case --random-sort $f | sponge $f
    end

    for f in (git --git-dir=/home/xk/j/.git/ ls-files | sed "s|^|/home/xk/j/|" | grep -i favorite)
        s sorted "$f"
    end
end
