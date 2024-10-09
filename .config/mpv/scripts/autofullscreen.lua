local state_file = mp.command_native({"expand-path", "~~/.fullscreen"})

local has_video_stream = nil
function check_video_stream()
    local i = 0
    local tracks_count = mp.get_property_number("track-list/count")
    while i < tracks_count do
        local track_type = mp.get_property(string.format("track-list/%d/type", i))
        local track_selected = mp.get_property(string.format("track-list/%d/selected", i))

        if track_selected == "yes" and track_type == "video" then
            has_video_stream = true
            return
        end

        i = i + 1
    end

    has_video_stream = false
end
mp.observe_property("track-list", "native", check_video_stream)

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

function save_fullscreen_state()
    -- print(has_video_stream)
    if not has_video_stream then
        return
    end

    local state = mp.get_property_native("fullscreen")
    local file = io.open(state_file, "w")
    if file and (state ~= nil) then
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
