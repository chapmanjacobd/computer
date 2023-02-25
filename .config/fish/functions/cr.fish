# Defined interactively
function cr
    pkill catt
    catt -d "Xylo and Orchestra" set_default
    catt volume 0 && catt volume 55
    catt stop
end
