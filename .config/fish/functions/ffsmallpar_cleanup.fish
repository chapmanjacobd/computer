# Defined via `source`
function ffsmallpar_cleanup
    ~/d/69_Taxes_Keep/
    for f in (cat ~/ffsmallpar_errors.txt)
        set mkv (echo $f | path change-extension small.mkv )

        if test -e $f -a -e $mkv
            trash-put $f
        end

        if not test -e $mkv
            echo $f
        end
    end

end
