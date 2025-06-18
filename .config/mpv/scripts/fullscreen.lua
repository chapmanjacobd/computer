function toggle_fullscreen_and_focus()
    local is_fullscreen = mp.get_property_boolean("fullscreen")

    mp.commandv("cycle", "fullscreen")

    if is_fullscreen then
        mp.commandv("run", "fish", "-c", "focus_under_mouse")
x    else
        mp.commandv("run", "fish", "-c", "focus_follows_mouse")
    end
end

mp.add_key_binding('f', "toggle_fullscreen_and_focus", toggle_fullscreen_and_focus)
mp.add_key_binding('MBTN_LEFT_DBL', "toggle_fullscreen_and_focus", toggle_fullscreen_and_focus)
