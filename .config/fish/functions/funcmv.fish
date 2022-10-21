# Defined interactively
function funcmv --argument old new
    set funcdir ~/.config/fish/functions/
    sed "s|$old|$new|" -i $funcdir/$old.fish
    mv $funcdir/$old.fish $funcdir/$new.fish
end
