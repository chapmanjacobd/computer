function _screen.size
    # Bounding box of the enabled outputs in logical (compositor) pixels.
    if test "$XDG_SESSION_TYPE" = wayland; and command -q kscreenctl
        kscreenctl list-outputs --json 2>/dev/null |
            jq -r '
                [.[] | select(.enabled and .position != null and .mode != null)
                 | {x: .position.x, y: .position.y,
                    w: (.mode.resolution.width / .scale),
                    h: (.mode.resolution.height / .scale)}]
                | if length == 0 then "0 0"
                  else "\(map(.x + .w) | max | round) \(map(.y + .h) | max | round)"
                  end
            '
        return
    end

    if command -q xdotool
        xdotool getdisplaygeometry
    end
end
