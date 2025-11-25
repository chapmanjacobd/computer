# Defined interactively
function path.withsuffix
    set -l orig_ext (path extension "$argv[1]")
    path change-extension "$argv[2]$orig_ext" "$argv[1]"
end
