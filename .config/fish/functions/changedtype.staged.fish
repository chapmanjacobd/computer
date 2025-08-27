# Defined interactively
function changedtype.staged
    git status --porcelain --short $argv | awk 'substr($0, 1, 1) == "T" && substr($0, 2, 1) == " " {print substr($0, 4)}' | string unescape --style=script
end
