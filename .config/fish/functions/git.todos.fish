# Defined interactively
function git.todos
    git ls-tree -r -z --name-only HEAD -- . | xargs -0 -n1 git blame -c | grep TODO | sort -t\t -k3
end
