# Defined via `source`
function rdp
    sdl-freerdp -authentication -encryption /v:localhost:35589 +clipboard /network:broadband-low -audio /smart-sizing /workarea +auto-reconnect /rfx /gfx:AVC420,thin-client,progressive,rfx -encryption -decorations /compression-level:2
end
