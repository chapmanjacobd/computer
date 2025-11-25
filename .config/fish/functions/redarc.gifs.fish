# Defined interactively
function redarc.gifs
    zstdcat $argv | jq -r 'select(.score > 7) | .url' | grep -iE 'gfycat.com|giphy.com'
end
