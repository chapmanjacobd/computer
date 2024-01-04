# Defined interactively
function substack
    mkdir ~/d/library/datasets/social/substack/
    ~/d/library/datasets/social/substack/
    set db ~/d/library/datasets/social/substack/(path dirname $argv | sed 's|https://||' | string replace -a / -).db
    lb substack $db $argv
    ~/j/social/
    lb export-text $db
end
