# Defined in /home/xk/.config/fish/functions/morganize.fish @ line 1
function morganize
    for f in ~/.config/fish/functions/*.fish
        fish_indent -w $f
    end

    for f in ~/mc/*.txt
        sort --unique --stable --ignore-case $f | sed '/^$/d' | sponge $f
    end

    for f in (fd -elist . ~/j/)
        s sorted "$f"
    end

    for f in ~/j/lists/people.*list
        dedupe "$f" | sort_by_last_name.py | sponge "$f"
    end
end
