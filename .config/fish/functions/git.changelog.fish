function git.changelog --description 'Prints git log in a way convenient for writing release notes' --argument range

    test -n "$range"; or set range (git describe --abbrev=0)".."

    git --no-pager log --reverse --format="* %s" $range
end
