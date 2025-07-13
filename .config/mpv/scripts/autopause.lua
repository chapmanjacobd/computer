local function on_focus_change(name, value)
    if mp.get_property("video") == "no" or not mp.get_property_native("fullscreen") then
        return
    end

    if value == true then -- mpv window is focused
        mp.set_property_bool("pause", false)
    else -- mpv window lost focus
        mp.set_property_bool("pause", true)
    end
end

mp.observe_property("focused", "bool", on_focus_change)
