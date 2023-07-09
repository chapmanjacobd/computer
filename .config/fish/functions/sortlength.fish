# Defined interactively
function sortlength
    perl -e 'print sort { length($a) <=> length($b) } <>'
end
