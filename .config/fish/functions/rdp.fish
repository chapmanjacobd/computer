# Defined via `source`
function rdp
    xfreerdp -authentication +clipboard +auto-reconnect -audio -decorations /v:/run/user/1000/rdp /network:broadband-low /clipboard:direction-to:all /smart-sizing /workarea /rfx /gfx:AVC420,thin-client,progressive,rfx /compression-level:2
end
