# Defined interactively
function resolution --description 'Current resolution'
    if _is_wayland; and command -q kscreenctl
        kscreenctl list-outputs --json 2>/dev/null |
            jq -r '.[] | select(.enabled and .mode != null) | "\(.mode.resolution.width)x\(.mode.resolution.height)"'
        return
    end

    xrandr | grep \* | lines.coln 1
end
