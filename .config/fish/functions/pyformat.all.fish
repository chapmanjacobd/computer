# Defined interactively
function pyformat.all
    ruff check . --fix --preview && pycln --all . && ssort && isort . && black --exclude=__pypackages__ .
end
