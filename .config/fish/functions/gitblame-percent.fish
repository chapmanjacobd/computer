# Defined in /home/xk/.config/fish/functions/gitblame-percent.fish @ line 2
function gitblame-percent --argument file
    set line_count (wc -l $file | cut -d' ' -f1)
    set authors (git blame --line-porcelain "$file" | grep "^author " | desc)

    for author in $authors
        set author_count (echo $author | sed 's| author.*$||')

        printf (echo $author | sed 's|^.*author ||')
        printf ' (%s%s)\n' (math -s1 "$author_count/$line_count * 100") '%'
    end
end
