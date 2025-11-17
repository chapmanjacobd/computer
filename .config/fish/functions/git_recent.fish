function git_recent
    for line in (git log --format="%H %P")
        set parts (string split ' ' $line)
        set commit $parts[1]
        set parents $parts[2..-1]

        for parent in $parents
            git diff $commit $parent
        end
    end
end
