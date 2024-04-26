# Defined interactively
function to_fgb
    for f in $argv
        ogr2ogr (path change-extension .fgb "$f") "$f" -skipfailures
        and trash "$f"
    end
end
