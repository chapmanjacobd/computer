# Defined interactively
function cr
    catt -d (lt.device) stop
    pkill catt
    catt -d (lt.device) volume 0 && catt -d (lt.device) volume 30
    catt -d (lt.device) stop
end
