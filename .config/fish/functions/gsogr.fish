# Defined interactively
function gsogr
    ogrinfo -al -geom=NO (string replace gs:// /vsigs/ -- $argv)
end
