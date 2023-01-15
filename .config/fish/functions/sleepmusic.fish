# Defined interactively
function sleepmusic
    catt -d "Bedroom pair" set_default
    fish -c '~/lb/ && lb listen -L 99 -cast -cast-to "Bedroom pair" -s relax' &
    sleep 8
    catt volume 25
    sleep 2700
    lt-stop
    catt -d "Xylo and Orchestra" set_default
end
