function playSomething --argument genre manyMult
    set many (default $manyMult 1)
    cd ~/Music/
    set files (filesDeep | fileTypeAudio | shuf -n (math "100*$many") | filterByGenre $genre)
    mpv --input-ipc-server=/tmp/mpvsocket --shuffle --no-audio-display $files
end
