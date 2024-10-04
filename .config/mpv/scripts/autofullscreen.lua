local state_file = mp.command_native({"expand-path", "~~/.fullscreen"})


function load_fullscreen_state()
    local file = io.open(state_file, "r")
    if file then
        local state = file:read("*l") -- read the whole line
        file:close()

        if state ~= nil then
            mp.set_property("fullscreen", state)
        end
    end
end

function has_video_stream()
    local tracks = mp.get_property_native("track-list")
    for _, track in ipairs(tracks) do
        if track.type == "video" then
            return true
        end
    end
    return false
end

function save_fullscreen_state()
    local state = mp.get_property_native("fullscreen")
    local file = io.open(state_file, "w")
    if file and (state ~= nil) and has_video_stream() then
        if state then
            file:write("yes")
        else
            file:write("no")
        end
        file:close()
    end
end

if not mp.get_property_bool("option-info/fullscreen/set-from-commandline") then
    load_fullscreen_state()
    mp.register_event("shutdown", save_fullscreen_state)
end
