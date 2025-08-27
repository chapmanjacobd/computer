# Defined interactively
function funcmv --argument old new
    set funcdir ~/.config/fish/functions
    sed "s|\b$old\b|$new|" -i $funcdir/*.fish
    mv $funcdir/$old.fish $funcdir/$new.fish
    echo abbrsave $old $new
end
