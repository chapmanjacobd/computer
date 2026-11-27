# Defined interactively
function ps.resume --wraps='kill'
    kill -CONT $argv
end
