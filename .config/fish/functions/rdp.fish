# Defined via `source`
function rdp
    expect -c '
set timeout -1
spawn xfreerdp -authentication +auto-reconnect /network:auto -audio -decorations /v:pakon.curl-amberjack.ts.net:35589 /smart-sizing /workarea /bpp:16 /rfx /gdi:hw /gfx:AVC420,rfx /clipboard
expect "Domain:"
send "\r"
expect "Password:"
send "\r"
expect eof
'
end
