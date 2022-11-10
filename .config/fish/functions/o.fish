# Defined in /tmp/fish.fnrMVk/o.fish @ line 2
function o
    xdg-open $argv & disown
    #disown (jobs -p)
    #exit
end
