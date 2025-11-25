# Defined in /tmp/fish.sUt5Y8/tzst.fish @ line 2
function files.to.tzst
    set target (string replace --regex '/$' '' $argv)
    tar cf "$target".tzst -I zstd "$target"
    and trash "$target"
end
