# Defined via `source`
function rdp
    expect -c '
set timeout -1
spawn xfreerdp -authentication +auto-reconnect /network:auto -audio -decorations /v:'$argv' /smart-sizing /workarea /clipboard /gfx:avc420,mask:0x1e0
expect "Domain:"
send "\r"
expect "Password:"
send "\r"
expect eof
'
end
