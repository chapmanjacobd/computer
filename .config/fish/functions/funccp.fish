# Defined interactively
function funccp --argument old new
    functions -c $old $new
    funcsave $new
    r
end
