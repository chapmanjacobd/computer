function toggle_fullscreen_and_focus()
    local was_fullscreen = mp.get_property("fullscreen") == "yes"

    mp.commandv("cycle", "fullscreen")

    if was_fullscreen then
        mp.commandv("run", "fish", "-c", "focus_follows_mouse")
    else
        mp.commandv("run", "fish", "-c", "focus_under_mouse")
    end
end

mp.add_key_binding('f', "toggle_fullscreen_and_focus", toggle_fullscreen_and_focus)
mp.add_key_binding('MBTN_LEFT_DBL', "toggle_fullscreen_and_focus", toggle_fullscreen_and_focus)
