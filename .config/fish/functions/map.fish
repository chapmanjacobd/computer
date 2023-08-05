# Defined via `source`
function map
    for f in $argv[2..-1]
        echo $f
        $argv[1] "$f"
    end
end
