function sendroidmusic
    adb push (find ~/Music/MusicLibrary/ -type f | shuf -n2000) /storage/self/primary/Music
end
