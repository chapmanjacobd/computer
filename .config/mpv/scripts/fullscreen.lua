function toggle_fullscreen_and_focus()
    local was_fullscreen = mp.get_property("fullscreen") == "yes"

    mp.commandv("cycle", "fullscreen")

    if was_fullscreen then
        mp.commandv("run", "fish", "-c", "kwin.FocusFollowsMouse")
    else
        mp.commandv("run", "fish", "-c", "kwin.FocusUnderMouse")
    end
end

mp.add_key_binding('f', "toggle_fullscreen_and_focus", toggle_fullscreen_and_focus)
mp.add_key_binding('MBTN_LEFT_DBL', "toggle_fullscreen_and_focus", toggle_fullscreen_and_focus)

mp.observe_property("eof-reached", "bool", function(name, value)
    if value then
        mp.set_property_native("fullscreen", false)
    end
end)
