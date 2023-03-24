# Defined via `source`
function m
    for f in $argv[2..-1]
        echo $f
        $argv[1] "$f"
    end
end
