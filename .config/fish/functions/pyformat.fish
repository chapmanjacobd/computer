# Defined via `source`
function pyformat
    for file in $argv
        ssort $file && isort --profile google --line-length=120 $file && black --line-length=120 --skip-string-normalization $file
    end
end
