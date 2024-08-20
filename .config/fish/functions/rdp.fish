# Defined interactively
function rdp
    sdl-freerdp -authentication /v:localhost:35589 +clipboard /network:auto /rfx /gfx:rfx /floatbar:sticky:off +fonts /bpp:32 /audio-mode:0 +aero +window-drag /size:2880x1724 /tune:FreeRDP_HiDefRemoteApp:true,FreeRDP_GfxAVC444v2:true,FreeRDP_GfxH264:true
end
