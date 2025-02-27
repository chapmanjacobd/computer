# Defined via `source`
function matchmv
    set target_folder $argv[1]
    set substrings $argv[2..-1]

    mkdir -p $target_folder

    for dir in */
        if test -d $dir
            set dirname (basename $dir)
            set match false

            for substring in $substrings
                if string match -q "*$substring*" $dirname
                    set match true
                    break
                end
            end

            if $match
                mv $dir $target_folder
            end
        end
    end
end
