# Defined interactively
function gdalinfo.gcs
    gdalinfo (string replace gs:// /vsigs/ -- $argv)
end
