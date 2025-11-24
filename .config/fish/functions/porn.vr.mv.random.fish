# Defined interactively
function porn.vr.mv.random
    ls ~/quest/Movies/
    if confirm
        mv ~/quest/Movies/* ~/d/library/porn/vr/
        fd -tf --max-results=3 . ~/d/check/porn/vr/ | xargs -I{} mv {} ~/quest/Movies/
    end
end
