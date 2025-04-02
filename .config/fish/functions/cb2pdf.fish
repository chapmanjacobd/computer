# Defined interactively
function cb2pdf
    set outpath (mktemp --suffix .pdf)

    pandoc -o $outpath (cb | psub -s md) -V pagestyle=empty
    dragondrop --on-top --all-compact $outpath
end
