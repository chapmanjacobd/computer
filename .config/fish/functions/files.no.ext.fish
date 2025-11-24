# Defined interactively
function files.no.ext
    find . -not \( -wholename './.git' -prune \) -type f ! -name '*.*' $argv
end
