# Defined via `source`
function cb.to.pdf
    set outpath (mktemp /tmp/(datestamp)_XXX --suffix=.pdf --dry-run)

    pandoc -o $outpath (cb | psub -s md) -V pagestyle=empty
    dragondrop --on-top --all-compact $outpath
end
