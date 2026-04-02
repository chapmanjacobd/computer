# Defined interactively
function git.eol.ignore
    git config --local core.autocrlf false
    git config --local core.safecrlf false
    git config --local core.text false
    # echo '* -text' >> .git/info/attributes
end
