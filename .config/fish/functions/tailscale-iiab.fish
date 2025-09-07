# Defined via `source`
function tailscale-iiab
    tailscale --socket="$HOME/.local/iiab/tailscale/foo.sock" $argv
end
