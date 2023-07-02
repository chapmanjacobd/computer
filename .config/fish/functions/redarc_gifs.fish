# Defined interactively
function redarc_gifs
    zstdcat (fd -eZST) | jq -r 'select(.score > 7) | .url' | grep -iE 'gfycat.com|giphy.com'
end
