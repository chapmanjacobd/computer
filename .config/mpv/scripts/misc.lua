-- load-script ~/.config/mpv/scripts/misc.lua
-- hide subs if same as audio (similar to --subs-with-matching-audio)
local selected_tracks = {}

function get_selected_tracks()
    local i = 0
    local tracks_count = mp.get_property_number("track-list/count")
    while i < tracks_count do
        local track_type = mp.get_property(string.format("track-list/%d/type", i))
        local track_index = mp.get_property_number(string.format("track-list/%d/ff-index", i))
        local track_selected = mp.get_property(string.format("track-list/%d/selected", i))
        local track_lang = mp.get_property(string.format("track-list/%d/lang", i))
        local track_external = mp.get_property(string.format("track-list/%d/external", i))
        local track_codec = mp.get_property(string.format("track-list/%d/codec", i))

        if track_selected == "yes" then
            selected_tracks[track_type] = track_lang
        end

        i = i + 1
    end
end

function dump(o)
    if type(o) == 'table' then
        local s = '{ '
        for k, v in pairs(o) do
            if type(k) ~= 'number' then
                k = '"' .. k .. '"'
            end
            s = s .. '[' .. k .. '] = ' .. dump(v) .. ' '
        end
        return s .. '} '
    else
        return tostring(o)
    end
end

function misc(name, value)
    get_selected_tracks()
    print(dump(selected_tracks))
    mp.set_property('sub-visibility', 'yes')
    if (selected_tracks['audio'] ~= nil) and (selected_tracks['audio'] == selected_tracks['sub']) then
        mp.set_property('sub-visibility', 'no')
    end
end

mp.observe_property('track-list', "native", misc)
