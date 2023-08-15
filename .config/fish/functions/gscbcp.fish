# Defined interactively
function gscbcp
    for l in (cb)
        gsutil -m cp $l\* .
    end
end
