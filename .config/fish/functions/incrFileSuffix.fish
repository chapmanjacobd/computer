# Defined in - @ line 2
function incrFileSuffix
    for file in $argv
        set match (string match -e -r '(.+)\.(\d+)\.([^.]+)' $file)
        if test $status -eq 0
            set root $match[-3]
            set n (math $match[-2] + 1)
            set ext $match[-1]
        else
            set match (string match -e -r '(.+)\.([^.]+)' $file)
            if test $status -ne 0
                # file does not have a dot. what to do?
                return
            end
            set root $match[-2]
            set n 1
            set ext $match[-1]
        end
        if test $n -gt 31
            set n 1
        end
        if test $n -gt 30
            trash $file
        end
        mv -iv $file $root.$n.$ext
    end
end
