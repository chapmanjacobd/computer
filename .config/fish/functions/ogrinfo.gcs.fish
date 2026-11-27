# Defined interactively
function ogrinfo.gcs --wraps='ogrinfo'
    ogrinfo -al -geom=NO (string replace gs:// /vsigs/ -- $argv)
end
