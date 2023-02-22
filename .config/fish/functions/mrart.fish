# Defined interactively
function mrart
    fd --max-results=50 -tf . ~/d/91_New_Art/ -0 | xargs -0 -I{} mv "{}" ~/d/90_Now_Viewing/
end
