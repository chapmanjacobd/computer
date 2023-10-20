# Defined via `source`
function gitcommitbefore
    git rev-list --max-count=1 --before=(date -d "$argv" +"%Y-%m-%d") HEAD
end
