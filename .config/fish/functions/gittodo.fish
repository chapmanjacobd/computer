# Defined interactively
function gittodo
    git --no-pager diff -U0 main | grep '^+.*TODO' | sed 's/^+//' | git --no-pager grep -nFf - 2>/dev/null
end
