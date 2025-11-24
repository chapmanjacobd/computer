function commandline.last.cmd --argument index
    history --prefix func | string replace -- ' -s ' ' ' | awk 'NF>1' | row 1 | lines.coln 2
end
