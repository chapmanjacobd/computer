# Defined interactively
function dl.substack --wraps='lb'
    mkdir ~/lb/sites/social/substack/
    ~/lb/sites/social/substack/
    set db ~/lb/sites/social/substack/(path dirname $argv | sed 's|https://||' | string replace -a / -).db
    lb database add substack $db $argv
    ~/j/social/
    lb database export html $db
end
