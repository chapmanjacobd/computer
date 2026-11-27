# Defined interactively
function files.no.ext --wraps='find'
    find . -not \( -wholename './.git' -prune \) -type f ! -name '*.*' $argv
end
