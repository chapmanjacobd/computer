# Defined via `source`
function pairwise.diff
    set files (fd -tf . $argv | sort --stable)

    for i in (seq 2 (count $files))
        set prev_file $files[(math $i - 1)]
        set curr_file $files[$i]
        delta --syntax-theme GitHub --max-line-length 1024 $prev_file $curr_file
    end | delta
end
