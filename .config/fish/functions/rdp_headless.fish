# Defined interactively
function rdp_headless
    pkill Xvfb
    b Xvfb :99 -screen 0 1024x768x24
    sleep 2
    b DISPLAY=:99 rdpserve

    sleep 3
    DISPLAY=:99 dbus-run-session startplasma

    pkill freerdp-shadow-cli
    pkill Xvfb
end
