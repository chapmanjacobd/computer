# Defined interactively
function gscbdl
    for l in (cb)
        gsutil -m cp $l\* .
    end
end
