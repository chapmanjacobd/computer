# Defined interactively
function git.push.nothing
    git remote add origin DISABLED
    git remote set-url --push origin DISABLED
    git config --local push.default nothing
end
