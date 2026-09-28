function lt.wakeup
    catt -d (lt.device) volume 1
    b lt -c (lt.device) sync/audio
    catt.volume.ramp 25
end
