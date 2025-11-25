# Defined interactively
function git.remote.server
    git remote remove origin
    set user (id -un)
    git remote add server ssh://$user@unli.xyz/home/$user/github/(path basename (pwd))/
    git branch --set-upstream-to=server/main main
    git fetch
end
