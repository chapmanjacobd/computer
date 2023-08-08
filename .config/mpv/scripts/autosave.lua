-- autosave.lua
--
-- Periodically saves "watch later" data during playback, rather than only saving on quit.
-- This lets you easily recover your position in the case of an ungraceful shutdown of mpv (crash, power failure, etc.).
local mp = require 'mp'

local function save() mp.command("write-watch-later-config") end

local function init()
    if not mp.get_property_bool("seekable", true) then return end
    if mp.get_property_number("duration", 0) < 420 then return end

    local save_period_timer = mp.add_periodic_timer(60, save)

    local function pause(_, paused)
        if paused then
            save_period_timer:stop()
        else
            save_period_timer:resume()
        end
    end

    mp.observe_property("pause", "bool", pause)
end

mp.register_event("file-loaded", init)
