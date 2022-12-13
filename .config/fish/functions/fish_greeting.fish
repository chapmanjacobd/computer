# Defined in /tmp/fish.1r7oen/fish_greeting.fish @ line 2
function fish_greeting
    cat /proc/loadavg | cut -d' ' -f 2
end
