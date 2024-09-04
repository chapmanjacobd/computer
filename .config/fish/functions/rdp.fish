# Defined via `source`
function rdp
    expect -c '
set timeout -1
spawn xfreerdp -authentication +clipboard +auto-reconnect -audio -decorations /v:127.0.0.1:35589 /network:broadband-low /clipboard:direction-to:all /smart-sizing /workarea /bpp:16 /compression-level:2 /rfx /gdi:hw
expect "Domain:"
send "\r"
expect "Password:"
send "\r"
expect eof
'
end
