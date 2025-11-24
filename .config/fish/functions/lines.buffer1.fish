# Defined interactively
function lines.buffer1
    perl -ne 'print $l;$l=$_;END{print $l}'
end
