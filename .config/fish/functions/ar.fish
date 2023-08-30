# Defined in /tmp/fish.sUt5Y8/ar.fish @ line 2
function ar
    set target (string replace '/' '' $argv)
    zip -qr "$target".zip "$target"; and trash-put "$target"
end
