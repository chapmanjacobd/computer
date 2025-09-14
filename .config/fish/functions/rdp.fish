# Defined via `source`
function rdp
    expect -c '
set timeout -1
spawn xfreerdp -authentication +auto-reconnect -audio -decorations /gdi:sw /network:auto /v:'$argv' /workarea /smart-sizing /clipboard
expect "Domain:"
send "\r"
expect "Password:"
send "\r"
interact
expect eof
'
end
