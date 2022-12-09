# Defined via `source`
function pyformat
    ssort $argv && isort --profile black --line-length=120 $argv && black --line-length=120 --skip-string-normalization $argv
end
