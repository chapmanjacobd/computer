# Defined in - @ line 2
function playSomethingReturnFiles --argument genre manyMult
    set many (default $manyMult 1)
    filesDeep ~/Music/ | fileTypeAudio | shuf -n (math "100*$many") | filterByGenre $genre
end
