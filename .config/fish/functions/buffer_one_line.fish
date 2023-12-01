# Defined interactively
function buffer_one_line
    perl -ne 'print $l;$l=$_;END{print $l}'
end
