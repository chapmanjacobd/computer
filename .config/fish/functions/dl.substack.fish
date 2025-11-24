# Defined interactively
function dl.substack
    mkdir ~/lb/sites/social/substack/
    ~/lb/sites/social/substack/
    set db ~/lb/sites/social/substack/(path dirname $argv | sed 's|https://||' | string replace -a / -).db
    lb dl.substack $db $argv
    ~/j/social/
    lb export-text $db
end
