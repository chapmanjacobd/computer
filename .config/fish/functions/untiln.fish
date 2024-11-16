# Defined interactively
function untiln --description 'untiln <count> <command>'
    for i in (seq 1 $argv[1])
        if fish -c (string join -- ' ' (string escape -- $argv[2..-1]))
            return
        end
    end
end
