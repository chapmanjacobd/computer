# Defined interactively
function paths.git.blame
    for f in (git grep --full-name --cached -Il '') # skip binary files
        printf "%s\t%s\n" "$f" (gitblame-percent "$f" | string join ', ')
    end | column -t

    printf '\nCommit summary:\n'
    git shortlog -ns
end
