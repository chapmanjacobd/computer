# Defined interactively
function mv-ln --argument from to
    mv $from $to
    ln -s $to (string replace -r '/$' '' $from)
end
