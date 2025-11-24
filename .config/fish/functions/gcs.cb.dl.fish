# Defined interactively
function gcs.cb.dl
    for l in (cb)
        gsutil -m cp $l\* .
    end
end
