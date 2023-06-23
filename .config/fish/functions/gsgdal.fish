# Defined interactively
function gsgdal
    gdalinfo (string replace gs:// /vsigs/ -- $argv)
end
