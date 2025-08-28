# Defined interactively
function renamed --wraps='git status'
    git status --porcelain --short $argv | awk '/^R/ {print $NF}' | string unescape --style=script
end
