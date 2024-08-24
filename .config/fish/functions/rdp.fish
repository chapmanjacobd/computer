# Defined via `source`
function rdp
    expect -c '
set timeout -1
spawn xfreerdp -authentication +clipboard +auto-reconnect -audio -decorations /v:/run/user/1000/rdp /network:broadband-low /clipboard:direction-to:all /smart-sizing /workarea /rfx /gfx:AVC420,thin-client,progressive,rfx /compression-level:2
expect "Domain:"
send "\r"
expect "Password:"
send "\r"
expect eof
'
end
