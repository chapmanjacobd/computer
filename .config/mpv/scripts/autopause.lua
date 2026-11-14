local pause_delay = 0.5
local pause_timer = nil
local seen_focus = false

local function eligible()
    return mp.get_property("video") ~= "no"
        and mp.get_property_native("fullscreen")
end

local function pause_if_still_unfocused()
    pause_timer = nil
    if not eligible() or mp.get_property_native("focused") then
        return
    end
    mp.set_property_bool("pause", true)
end

local function on_focus_change(name, focused)
    if focused == nil then
        return
    end

    if pause_timer then
        pause_timer:kill()
        pause_timer = nil
    end

    if focused then
        seen_focus = true
        if eligible() then
            mp.set_property_bool("pause", false)
        end
    elseif seen_focus and eligible() then
        pause_timer = mp.add_timeout(pause_delay, pause_if_still_unfocused)
    end
end

mp.observe_property("focused", "bool", on_focus_change)
