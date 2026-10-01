# Defined interactively
function git.push.nothing
    git remote add origin DISABLED
    git remote set-url --push origin DISABLED
    git config --local remote.origin.skipFetchAll true
    git config --local push.default nothing
end
