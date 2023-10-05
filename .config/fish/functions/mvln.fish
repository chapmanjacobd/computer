# Defined interactively
function mvln --argument from to
    mv $from $to
    ln -s $to (string replace -r '/$' '' $from)
end
