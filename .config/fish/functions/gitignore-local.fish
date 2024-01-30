# Defined interactively
function gitignore-local
    echo $argv >>.git/info/exclude
end
