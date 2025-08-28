# Defined interactively
function unmerged --wraps='git status'
    git status --porcelain --short $argv | awk '$1 ~ /^(DD|AU|UD|UA|DU|AA|UU)/ {print substr($0, 4)}' | string unescape --style=script
end
