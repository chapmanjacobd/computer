# Defined via `source`
function rdp
    sdl-freerdp -authentication -encryption /v:/run/user/1000/rdp +clipboard /network:broadband-low -audio /smart-sizing /workarea +auto-reconnect /rfx /gfx:AVC420,thin-client,progressive,rfx -encryption -decorations /compression-level:2
end
