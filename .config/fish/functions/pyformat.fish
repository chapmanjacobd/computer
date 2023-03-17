# Defined via `source`
function pyformat
    for file in $argv
        ssort $file && isort --profile black -p atlasai.data_processor --line-length=120 $file && black --line-length=120 --skip-string-normalization $file
    end
end
