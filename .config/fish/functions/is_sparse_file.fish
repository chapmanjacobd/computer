# Defined via `source`
function is_sparse_file
    set actual_size (du --block-size=1 "$argv" | awk '{print $1}')
    set apparent_size (du --block-size=1 --apparent-size "$argv" | awk '{print $1}')

    if test $actual_size -eq $apparent_size
        return 1
    else
        return 0
    end
end
