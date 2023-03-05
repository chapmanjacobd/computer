# Defined interactively
function keepaud
    cp "$argv" ~/d/85_Inspiration/ffa/
    set f (basename "$argv")
    ffa "$HOME/d/85_Inspiration/ffa/$f"
    and /bin/rm "$argv"
end
