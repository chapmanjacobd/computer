# Defined via `source`
function wget.force.suffix --argument ext
    set fname (mktemp --suffix .$ext -p $HOME/Downloads/)
    wget --no-verbose -O $fname $argv[2..-1] >/dev/null
    echo $fname
end
