# Defined interactively
function cr
    pkill catt
    set_catt_default "Xylo and Orchestra"
    catt volume 0 && catt volume 40
    catt stop
end
