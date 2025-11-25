# Defined interactively
function git.ignore.get --argument lang
    curl -L https://raw.githubusercontent.com/github/gitignore/refs/heads/main/$lang.gitignore -o .gitignore
end
