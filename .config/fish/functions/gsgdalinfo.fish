# Defined interactively
function gsgdalinfo
    gdalinfo (string replace gs:// /vsigs/ -- $argv)
end
