# Defined in /home/xk/.config/fish/functions/gitblame-percent.fish @ line 2
function git.blame.share --argument file
    set line_count (wc -l $file | cut -d' ' -f1)
    set authors (git blame --line-porcelain "$file" | grep "^author " | desc)

    if test $line_count -eq 0
        return
    end

    for author in $authors
        set author_count (echo $author | sed 's| author.*$||')

        printf (echo $author | sed 's|^.*author ||')
        printf ' (%s%s)\n' (math -s0 "$author_count/$line_count * 100") '%'
    end
end
