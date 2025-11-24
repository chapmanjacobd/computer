# Defined via `source`
function image-folder-ask-keep
    for dir in $argv
        for d in (fd . -td "$dir" | sort.length | tac)
            echo "$d"
            feh -q -F --hide-pointer --sort filename --on-last-slide resume -G --auto-zoom --zoom max --draw-tinted --image-bg black --scale-down -D -3 "$d"

            if confirm keep
                b lb relmv "$d" ~/d/library/porn/image/
            else
                b trash "$d"
            end
        end
    end
end
