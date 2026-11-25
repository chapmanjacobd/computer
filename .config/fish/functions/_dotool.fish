# Send a batch of dotool actions to one uinput instance. Callers write
# actions such as "key ctrl+c" or "mouseto 0.5 0.5" on stdin.
function _dotool
    if not command -q dotool
        echo "dotool: not found; install it with 'sudo dnf install dotool'" >&2
        return 127
    end

    set -l layout us
    set -l variant
    if command -q kreadconfig6
        set -l layouts (kreadconfig6 --file kxkbrc --group Layout --key LayoutList 2>/dev/null | string split ',')
        set -l variants (kreadconfig6 --file kxkbrc --group Layout --key VariantList 2>/dev/null | string split ',')
        test -n "$layouts[1]"; and set layout $layouts[1]
        test -n "$variants[1]"; and set variant $variants[1]
    end

    set -lx DOTOOL_XKB_LAYOUT $layout
    test -n "$variant"; and set -lx DOTOOL_XKB_VARIANT $variant
    command dotool
end
