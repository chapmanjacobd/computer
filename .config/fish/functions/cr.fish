# Defined interactively
function cr
    catt stop
    pkill catt
    set_catt_default "Xylo and Orchestra"
    catt volume 0 && catt volume 14
    catt stop
end
