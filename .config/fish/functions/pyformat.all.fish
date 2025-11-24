# Defined interactively
function pyformat.all
    pycln --all . && ssort && isort . && black --exclude=__pypackages__ .
end
