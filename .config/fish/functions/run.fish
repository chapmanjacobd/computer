# Defined interactively
function run -w setsid
    setsid -f $argv 2>/dev/null
end
