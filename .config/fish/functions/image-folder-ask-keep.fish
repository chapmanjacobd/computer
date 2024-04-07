# Defined via `source`
function image-folder-ask-keep
    for dir in $argv
        for d in (fd . -td "$dir")
            feh -q -F --hide-pointer --sort filename --on-last-slide resume -G --auto-zoom --zoom max --draw-tinted --image-bg black --scale-down -D -3 "$d"
            if not confirm keep
                trash-put "$d"
            end
        end
    end
end
