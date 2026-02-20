# Defined interactively
function dl.file --argument-names url
    set -l ext (string match -r '\.[^.]+$' $url)
    set -l tmp_file (mktemp --suffix=$ext)

    curl -sSL $url -o $tmp_file
    echo $tmp_file
end
