# Defined interactively
function gdalinfo.gcs --wraps='gdalinfo'
    gdalinfo (string replace gs:// /vsigs/ -- $argv)
end
