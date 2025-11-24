# Defined interactively
function vector.to.flatgeobuf
    for f in $argv
        ogr2ogr (path change-extension .fgb "$f") "$f" -skipfailures
        and trash "$f"
    end
end
