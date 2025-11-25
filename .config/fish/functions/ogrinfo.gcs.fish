# Defined interactively
function ogrinfo.gcs
    ogrinfo -al -geom=NO (string replace gs:// /vsigs/ -- $argv)
end
