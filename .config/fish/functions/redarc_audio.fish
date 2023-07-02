# Defined interactively
function redarc_audio
    zstdcat (fd -eZST) | jq -r 'select(.score > 7) | .url' | grep -iE 'archive.org|youtube.com|youtu.be|vimeo.com|mixcloud.com|soundcloud.com|soundgasm.net'
end
