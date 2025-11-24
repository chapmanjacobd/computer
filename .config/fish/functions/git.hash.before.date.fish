# Defined via `source`
function git.hash.before.date
    # git diff (git.hash.before.date Oct 10)
    git rev-list --max-count=1 --before=(date -d "$argv" +"%Y-%m-%d") HEAD
end
