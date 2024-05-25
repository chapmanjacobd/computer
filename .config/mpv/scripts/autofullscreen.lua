local state_file = mp.command_native({"expand-path", "~~/.fullscreen"})

function save_fullscreen_state()
    local state = mp.get_property_bool("fullscreen")
    local file = io.open(state_file, "w")
    if file then
        file:write(state and "yes" or "no")
        file:close()
    end
end

function load_fullscreen_state()
    local file = io.open(state_file, "r")
    if file then
        local state = file:read("*l") -- read the whole line
        file:close()
        if state == "yes" then
            mp.set_property("fullscreen", "yes")
        else
            mp.set_property("fullscreen", "no")
        end
    end
end

mp.register_event("shutdown", save_fullscreen_state)
mp.register_event("start-file", load_fullscreen_state)
