# Defined interactively
function lbformat
    pycln --all . && ssort && isort . && black --exclude=__pypackages__ .
end
