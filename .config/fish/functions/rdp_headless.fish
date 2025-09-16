# Defined interactively
function rdp_headless
    pkill Xvfb
    b Xvfb :99 -screen 0 1024x768x24
    DISPLAY=:99 rdpserve

    sleep 5
    DISPLAY=:99 dbus-run-session startplasma
end
