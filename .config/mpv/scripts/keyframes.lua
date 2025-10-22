-- mpv script: reload current file through ffmpeg bitstream filter
-- Keybinding example (in input.conf): F9 script-message reload-with-bsf
-- Filters out non-keyframes: -bsf:v noise=drop=not(key)
local mp = require "mp"
local utils = require "mp.utils"

local temp_path = nil
local ffmpeg_pid = nil

local function cleanup()
    if temp_path then
        os.remove(temp_path)
        temp_path = nil
    end
end

local function reload_to_keyframes()
    local path = mp.get_property("path")
    if not path then
        mp.osd_message("No file loaded")
        return
    end

    temp_path = utils.join_path("/tmp", "mpv_bsf.mp4")
    -- os.remove(temp_path)

    -- build ffmpeg command; spawn asynchronously
    local command_string = string.format("ffmpeg.keyframes.io '%s' '%s'", path, temp_path)
    local args = {"fish", "-c", command_string}
    ffmpeg_pid = mp.command_native_async({"run", unpack(args)},
                                         function(success, result, err)
        if not success then
            mp.osd_message("ffmpeg failed: " .. tostring(err))
            cleanup()
        end
    end)

    mp.set_property_number("time-pos", 0)
    -- replace playback
    mp.add_timeout(5, function()
        mp.commandv("loadfile", temp_path, "replace")
        mp.set_property_number("time-pos", 0)
        mp.register_event("shutdown", cleanup)
    end)
end

mp.add_key_binding(nil, "reload-to-keyframes", reload_to_keyframes)
