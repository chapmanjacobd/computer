local fade_duration = 0.1 -- 100 milliseconds for fade
local fade_steps = 10 -- Number of steps for fading (more steps = smoother fade)
local fade_interval = fade_duration / fade_steps

local function fade_out_volume(target_volume, current_step, start_volume)
    if current_step > fade_steps then
        mp.set_property("volume", target_volume) -- Ensure final volume is set precisely
        return
    end

    local current_volume = mp.get_property_native("volume")
    local step_size = (start_volume - target_volume) / fade_steps
    local new_volume = start_volume - (step_size * current_step)

    -- Ensure volume doesn't go below target or is exactly target on last step
    if target_volume < start_volume then -- Fading out
        new_volume = math.max(new_volume, target_volume)
    else -- Fading in
        new_volume = math.min(new_volume, target_volume)
    end

    mp.set_property("volume", new_volume)

    mp.add_timeout(fade_interval, function()
        fade_out_volume(target_volume, current_step + 1, start_volume)
    end)
end

local function fade_in_volume(target_volume, current_step, start_volume)
    if current_step > fade_steps then
        mp.set_property("volume", target_volume) -- Ensure final volume is set precisely
        return
    end

    local step_size = (target_volume - start_volume) / fade_steps
    local new_volume = start_volume + (step_size * current_step)

    mp.set_property("volume", new_volume)

    mp.add_timeout(fade_interval, function()
        fade_in_volume(target_volume, current_step + 1, start_volume)
    end)
end

local timer = nil
local threshold = 0.150

local function unmute_player()
    if mp.get_property_number("volume") == 0 then
        mp.set_property_number("volume", 80)
    end
    if mp.get_property_bool("pause") then
        mp.set_property_bool("pause", false)
    end
    timer = nil
end

local function on_focus_change(name, value)
    if mp.get_property("video") == "no" then
        return
    end

    if value == true then -- mpv window is focused
        if timer == nil then -- Start timer only if not already running
            timer = mp.add_timeout(threshold, unmute_player)
        end
    else -- mpv window lost focus
        if timer ~= nil then -- Cancel the timer if it's running
            timer:kill()
            timer = nil
        end

        if mp.get_property_native("fullscreen") == true then
            local current_volume = mp.get_property_native("volume")
            fade_out_volume(0, 1, current_volume)
            -- mp.set_property("volume", "0")
        end
    end
end

mp.observe_property("focused", "bool", on_focus_change)
