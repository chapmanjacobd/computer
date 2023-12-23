# Defined interactively
function mrquest
    ls ~/quest/Movies/
    if confirm
        mv ~/quest/Movies/* ~/d/68_Vr_Tv_Keep/
        fd --max-results=3 . ~/d/68_Vr_Tv/_new/ | xargs -I{} mv {} ~/quest/Movies/
    end
end
