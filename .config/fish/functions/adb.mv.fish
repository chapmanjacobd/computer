# Defined in - @ line 2
function adb.mv --wraps='adb'
    adb push $argv /storage/self/primary/Movies
    and trash $argv
end
