# Defined in /tmp/fish.sUt5Y8/ar.fish @ line 2
function ar
    set target (string replace '/' '' $argv)
    tar cf "$target".tzst -I zstd "$target"
    and trash "$target"
end
