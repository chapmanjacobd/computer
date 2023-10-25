# Defined via `source`
function pyformat
    for file in $argv
        pycln --all $file && ssort $file && isort --profile black -p atlasai --line-length=120 $file && black --line-length=120 --skip-string-normalization $file
    end
end
