# Defined via `source`
function search.copyq
    copyq eval -- "for(i=0; i<size(); ++i) print(str(read(i)) + '\\n\\n');" | ov
end
