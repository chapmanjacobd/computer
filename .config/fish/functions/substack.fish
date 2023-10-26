# Defined interactively
function substack
    ~/d/30_Computing/substack/
    set db ~/d/30_Computing/substack/(path dirname $argv | sed 's|https://||' | string replace -a / -).db
    lb substack $db $argv
    ~/j/social/
    lb export-text $db
end
