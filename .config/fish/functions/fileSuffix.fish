# Defined interactively
function fileSuffix
    path change-extension "$argv[1]" ".$argv[2].(path extension "$argv[1]")"
end
