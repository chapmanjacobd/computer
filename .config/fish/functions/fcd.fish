# Defined in /tmp/fish.W1zARV/fcd.fish @ line 2
function fcd
    cd (find -type d | fzf)
end
