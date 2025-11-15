# Defined interactively
function funcmv --argument old new
    set funcdir ~/.config/fish/functions
    sed "s|\b$old\b|$new|" -i $funcdir/*.fish ~/.local/share/fish/fish_history
    mv $funcdir/$old.fish $funcdir/$new.fish
    echo abbrsave $old $new
end
