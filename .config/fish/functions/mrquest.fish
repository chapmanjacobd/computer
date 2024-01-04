# Defined interactively
function mrquest
    ls ~/quest/Movies/
    if confirm
        mv ~/quest/Movies/* ~/d/archive/porn/vr/
        fd --max-results=3 . ~/d/dump/porn/vr/_new/ | xargs -I{} mv {} ~/quest/Movies/
    end
end
