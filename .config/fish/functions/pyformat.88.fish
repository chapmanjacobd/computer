# Defined interactively
function pyformat.88
    for file in $argv
        isort --profile black -p atlasai --line-length=88 $file && black --line-length=88 --skip-string-normalization $file
    end
end
