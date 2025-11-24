# Defined interactively
function art.mv.random
    fd --max-results=50 -tf . ~/d/dump/image/other/ -0 | xargs -0 -I{} mv "{}" ~/sync/image/other/
end
