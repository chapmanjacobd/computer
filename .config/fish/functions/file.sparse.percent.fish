# Defined interactively
function file.sparse.percent
    find $argv -type f -printf '%S\0%P\n' | awk -v FS='\0' '
        function abs(v) {return v < 0 ? -v : v}

        {printf "%.1f%%\t%s\n", abs(1-$1) * 100, $2}'
end
