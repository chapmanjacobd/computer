# Defined interactively
function smartctl.ls
    for var in $argv
        echo $var
        for dev in /dev/sd(seqalpha a z)
            if test -e $dev
                printf "$dev\t%s\n" (sudo smartctl -A $dev)
            end
        end | grep $var | sort -k 11 --numeric-sort
    end
end
