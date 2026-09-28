# Defined interactively
function audio.sleepmusic
    fish -c '~/lb/ && lb listen -L 99 -cast -cast-to "Bedroom" -s relax' &
    sleep 8
    catt -d Bedroom volume 25
    sleep 2700
    lt.stop
end
