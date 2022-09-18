-- Override mpv's default volume keybinds with decibel controls
-- Put this file (dbvol.lua) in ~/.config/mpv/scripts/
-- WARNING: positive gain values may cause clipping

-- Author: Romain "Artefact2" Dal Maso <romain.dalmaso@artefact2.com>
-- Released under the WTFPLv2

function round(n)
    -- https://stackoverflow.com/a/58411671
    return n + (2^52 + 2^51) - (2^52 + 2^51)
end

function volume_to_db(vol)
    -- assumes samples are multiplied by (vol/100)^3
    -- https://github.com/mpv-player/mpv/blob/master/player/audio.c#L161
    return 60.0 * math.log(vol / 100.0) / math.log(10.0)
end

function db_to_volume(db)
    return math.exp(math.log(10.0) * (db / 60.0 + 2))
end

function increase_db()
    g = round(volume_to_db(mp.get_property_number("volume"))) + 1
    mp.set_property_number("volume", db_to_volume(g))
    mp.osd_message(string.format("Gain: %+.2f dB", g))
end

function decrease_db()
    g = round(volume_to_db(mp.get_property_number("volume"))) - 1
    mp.set_property_number("volume", db_to_volume(g))
    mp.osd_message(string.format("Gain: %+.2f dB", g))
end

-- Override default controls, https://github.com/mpv-player/mpv/blob/master/etc/input.conf
mp.add_key_binding("9", "decrease-db", decrease_db, { repeatable = true })
mp.add_key_binding("/", decrease_db, { repeatable = true })
mp.add_key_binding("WHEEL_LEFT", decrease_db, { repeatable = true })
mp.add_key_binding("VOLUME_DOWN", decrease_db, { repeatable = true })

mp.add_key_binding("0", "increase-db", increase_db, { repeatable = true })
mp.add_key_binding("*", increase_db, { repeatable = true })
mp.add_key_binding("WHEEL_RIGHT", increase_db, { repeatable = true })
mp.add_key_binding("VOLUME_UP", increase_db, { repeatable = true })
