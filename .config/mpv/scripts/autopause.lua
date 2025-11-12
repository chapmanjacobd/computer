local pause_delay = 0.3
local pause_timer = nil

local function do_pause()
    if mp.get_property_bool("pause") == false then
        mp.set_property_bool("pause", true)
    end
    pause_timer = nil
end

local function on_focus_change(name, value)
    if mp.get_property("video") == "no" or not mp.get_property_native("fullscreen") then
        if pause_timer then
            pause_timer:kill()
            pause_timer = nil
        end
        return
    end

    if value == true then -- mpv window is focused
        if pause_timer then
            pause_timer:kill()
            pause_timer = nil
        else
            mp.set_property_bool("pause", false)
        end
    else
        if pause_timer then
            return
        end
        
        pause_timer = mp.add_timeout(pause_delay, do_pause)
    end
end

mp.observe_property("focused", "bool", on_focus_change)
