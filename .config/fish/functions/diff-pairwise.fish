# Defined via `source`
function diff-pairwise
    set files (fd -tf . $argv)

    for i in (seq 2 (count $files))
        set prev_file $files[(math $i - 1)]
        set curr_file $files[$i]
        delta --syntax-theme GitHub --max-line-length 1024 $prev_file $curr_file
    end | less -FSRXc
end
