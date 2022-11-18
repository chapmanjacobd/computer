# Defined interactively
function mrquest
    mv ~/quest/Movies/* ~/d/68_VR_TV_Keep/
    fd --max-results=3 . ~/d/68_VR_TV/_new/ | xargs -I{} mv {} ~/quest/Movies/
end
