# Defined interactively
function gitls-authors
    for f in (git grep --full-name --cached -Il '')
        printf "%s\t%s\n" "$f" (gitblame-percent "$f" | string join ', ')
    end | column -t

    echo Total
    git shortlog -ns
end
