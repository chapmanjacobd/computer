# Defined interactively
function audio.sleepmusic
    catt -d Bedroom set_default
    fish -c '~/lb/ && lb listen -L 99 -cast -cast-to "Bedroom" -s relax' &
    sleep 8
    catt volume 25
    sleep 2700
    lt-stop
    catt -d "Xylo and Orchestra" set_default
end
