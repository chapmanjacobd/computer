# Defined interactively
function ps.pause --wraps='kill'
    kill -STOP $argv
end
