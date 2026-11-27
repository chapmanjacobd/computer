# Defined interactively
function redarc.gifs --wraps='zstdcat'
    zstdcat $argv | jq -r 'select(.score > 7) | .url' | grep -iE 'gfycat.com|giphy.com'
end
