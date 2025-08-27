# Defined interactively
function renamed
    git status --porcelain --short | awk '/^R/ {print $NF}' | string unescape --style=script
end
