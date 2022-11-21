-- feel free to modify and/or redistribute as long as you give credit to the original creator; © 2022 Ben Kerman
local cfg = {
    default_state = true,
    seek_mode_default = false,
    min_skip_interval = 3,
    max_nonskip_interval = 7,
    speed_skip_speed = 2.5,
    lead_out = 1,
    speed_skip_speed_delta = 0.1,
    min_skip_interval_delta = 0.25
}
require("mp.options").read_options(cfg, nil, function(changes)
    if changes.default_state then toggle_script() end
    if changes.seek_mode_default then switch_mode() end
    if changes.min_skip_interval then set_min_interval(cfg.min_skip_interval) end
    if changes.speed_skip_speed then
        set_speed_skip_speed(cfg.speed_skip_speed)
    end
end)

local selected_tracks = {}
local active = cfg.default_state
local seek_skip = cfg.seek_mode_default
local skipping = false
local sped_up = false
local last_sub_end, next_sub_start

function calc_next_delay()
    -- hide subtitles, otherwise sub could briefly flash on screen when stepping
    local was_visible = mp.get_property_bool("sub-visibility")
    if was_visible then mp.set_property_bool("sub-visibility", false) end

    local initial_delay = mp.get_property_number("sub-delay")

    -- get time to next line by adjusting subtitle delay
    -- so that the next line starts at the current time
    mp.commandv("sub-step", "1")
    local new_delay = mp.get_property_number("sub-delay")
    mp.set_property_number("sub-delay", initial_delay)

    if was_visible then mp.set_property_bool("sub-visibility", true) end

    -- print('initial_delay', initial_delay, 'new_delay', new_delay)
    -- if the delay didn't change, the next line hasn't been demuxed yet
    -- (or there are no more lines)
    -- else calculate difference between previous delay and shifted delay
    if new_delay == initial_delay then
        return nil
    else
        return -(new_delay - initial_delay)
    end
end

-- SEEK SKIP --
-- Seek skip generally works by directly skipping to the calculated start
-- of the next line. If it is not available, the script repeatedly seeks
-- to the end of the demuxer cache until a line is found.

function end_seek_skip(next_sub_begin)
    mp.set_property_number("time-pos", next_sub_begin - cfg.lead_out)
    -- print('end_seek_skip end_skip')
    end_skip()
end

-- create timer that determines if the next line has been found and reacts accordingly
local seek_skip_timer
seek_skip_timer = mp.add_periodic_timer(128, function()
    if mp.get_property_bool("seeking") == false then
        seek_skip_timer:stop()
        local time_pos = mp.get_property_number("time-pos")
        local next_delay = calc_next_delay()
        if next_delay == nil then
            -- if no line found, seek to end of demuxer cache (potentially unstable!)
            local cache_duration = mp.get_property_number(
                                       "demuxer-cache-duration")
            local seek_time = cache_duration or 1
            mp.set_property_number("time-pos", time_pos + seek_time)
            seek_skip_timer:resume()
        else
            -- if line found, finish seek skip
            seek_skip_timer:kill()
            end_seek_skip(time_pos + next_delay)
            mp.set_property_bool("pause", false)
        end
    end
end)
-- make sure that the timer never fires while the script is being loaded
seek_skip_timer:kill()
seek_skip_timer.timeout = 0.05

function start_seek_skip()
    mp.unobserve_property(handle_tick)
    local next_delay = calc_next_delay()
    if next_delay ~= nil then
        -- if next line is visible seek immediately
        end_seek_skip(mp.get_property_number("time-pos") + next_delay)
    else
        mp.set_property_bool("pause", true)
        seek_skip_timer:resume()
    end
end

-- SPEED SKIP (mostly) --
-- Speed skip works by simply speeding up playback between the end of the last line
-- (+lead in) until the start of the next one (-lead out).
-- If the start of the next line is not known, playback is sped up and it's checked
-- on each tick (i.e. change of time-pos) if the next line has been loaded.

local initial_speed = mp.get_property_number("speed")
local initial_video_sync = mp.get_property("video-sync")
local start_idle = nil
function handle_tick(_, time_pos)
    -- time_pos might be nil after the file changes
    if time_pos == nil then return end

    if not sped_up and last_sub_end ~= nil and time_pos > last_sub_end then
        if seek_skip then
            start_seek_skip()
        else
            initial_speed = mp.get_property_number("speed")
            -- Setting video-sync to desync and then audio prevents audio issues
            -- after resetting speed back to its initial value.
            initial_video_sync = mp.get_property("video-sync")
            mp.set_property("video-sync", "desync")
            mp.set_property_number("speed", cfg.speed_skip_speed)
            sped_up = true
        end
    elseif next_sub_start == nil then
        -- no next line was found during blind skip
        local next_delay = calc_next_delay()
        if next_delay ~= nil then
            next_sub_start = time_pos + next_delay
        end
    elseif sped_up and time_pos > next_sub_start - cfg.lead_out then
        -- print('handle_tick end_skip')
        end_skip()
    elseif not sped_up and not seek_skip then
        if (start_idle == nil) or (start_idle > time_pos) then
            start_idle = time_pos
        end
        elapsed_idle = time_pos - start_idle
        -- print('elapsed_idle', elapsed_idle)
        if cfg.max_nonskip_interval < elapsed_idle then
            -- subtitle hasn't changed for n seconds so we speed up
            -- print('idle skip')
            last_sub_end = time_pos
        end
    end
end

-- INITIALIZATION/SHARED FUNCTIONALITY --

function start_skip()
    -- print('start_skip')
    skipping = true
    mp.observe_property("time-pos", "number", handle_tick)
end

function end_skip()
    -- mp.unobserve_property(handle_tick)
    skipping = false
    sped_up = false
    mp.set_property_number("speed", initial_speed)
    mp.set_property("video-sync", "audio")
    mp.set_property("video-sync", initial_video_sync)
    last_sub_end, next_sub_start = nil, nil
    start_idle = nil
end

function handle_sub_change(_, sub_end)
    if sub_end then
        start_idle = nil
    end

    if sub_end and (skipping or sped_up) then
        -- print('handle_sub_change end_skip')
        end_skip()
    elseif not sub_end and not skipping then
        local time_pos = mp.get_property_number("time-pos")
        local next_delay = calc_next_delay()

        -- print('handle_sub_change', sub_end, last_sub_end, time_pos, next_delay)
        last_sub_end = time_pos
        if next_delay ~= nil then
            if next_delay < cfg.min_skip_interval then
                return
            else
                next_sub_start = time_pos + next_delay
            end
        end
        start_skip()
    end
end

function get_selected_tracks()
    local i = 0
    local tracks_count = mp.get_property_number("track-list/count")
    while i < tracks_count do
        local track_type = mp.get_property(string.format("track-list/%d/type", i))
        local track_selected = mp.get_property(string.format("track-list/%d/selected", i))

        if track_selected == "yes" then
            selected_tracks[track_type] = true
        end

        i = i + 1
    end
end

function activate()
    get_selected_tracks()

    if (selected_tracks['video'] ~= nil) and (selected_tracks['sub'] ~= nil) then
        mp.observe_property("sub-end", "number", handle_sub_change)
        active = true
    else
        deactivate()
    end
end

function deactivate()
    seek_skip_timer:kill()
    end_skip()
    mp.unobserve_property(handle_sub_change)
    active = false
end

mp.observe_property('track-list', "native", activate)

-- CONFIG --

function toggle_script()
    if active then
        deactivate()
        mp.osd_message("Non-subtitle skip disabled")
    else
        activate()
        mp.osd_message("Non-subtitle skip enabled")
    end
end

mp.add_key_binding("Ctrl+v", "toggle", toggle_script)

function switch_mode()
    seek_skip = not seek_skip
    mp.osd_message("Seek skip " .. (seek_skip and "enabled" or "disabled"))
end

mp.add_key_binding("Ctrl+V", "switch-mode", switch_mode)

function set_speed_skip_speed(new_value)
    cfg.speed_skip_speed = new_value
    if skipping then mp.set_property_number("speed", new_value) end
    mp.osd_message("Skip speed: " .. new_value)
end

mp.add_key_binding("Ctrl+Alt+[", "decrease-speed", function()
    set_speed_skip_speed(cfg.speed_skip_speed - cfg.speed_skip_speed_delta)
end, {repeatable = true})

mp.add_key_binding("Ctrl+Alt+]", "increase-speed", function()
    set_speed_skip_speed(cfg.speed_skip_speed + cfg.speed_skip_speed_delta)
end, {repeatable = true})

function set_min_interval(new_value)
    cfg.min_skip_interval = new_value
    mp.osd_message("Minimum interval: " .. new_value)
end

mp.add_key_binding("Ctrl+Alt+-", "decrease-interval", function()
    set_min_interval(cfg.min_skip_interval - cfg.min_skip_interval_delta)
end, {repeatable = true})

mp.add_key_binding("Ctrl+Alt++", "increase-interval", function()
    set_min_interval(cfg.min_skip_interval + cfg.min_skip_interval_delta)
end, {repeatable = true})
