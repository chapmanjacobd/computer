# Defined via `source`
function mkexec.py
    for f in $argv
        if not grep -q '^#!' $f
            echo "#!/usr/bin/python3" | cat - $f | sponge $f
        end

        mkexec $f
    end
end
