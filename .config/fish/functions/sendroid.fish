# Defined in - @ line 2
function sendroid
    adb push $argv /storage/self/primary/Movies
    and trash $argv
end
