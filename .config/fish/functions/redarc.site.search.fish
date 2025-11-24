# Defined interactively
function redarc.site.search --argument site
    for f in (fd -eZST)
        zstdcat $f | head -10000 | jq -r 'select(.score > 7) | .url' | grep -vEi '^/r/|^/user/|\. |^null$|^$' | grep -i $site | head
    end
end
