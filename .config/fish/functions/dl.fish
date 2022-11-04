# Defined interactively
function dl
    b dl-get-sounds 82_Audiobooks
    b dl-get-sounds 83_ClassicalComposers
    b dl-get-sounds 81_New_Music
    b dl-get-videos 71_Mealtime_Videos $argv
    b dl-get-videos 75_MovieQueue $argv --no-match-filter --match-filter 'requested_subtitles & duration > 1440' --reject-title="Um Himmels|Two Dads"
    b dl-get-videos 96_Weird_History $argv
    b dl-get-photos 91_New_Art
    b dl-get-sounds 63_Sounds
    wait
    dl-get-videos 69_Taxes $argv
    dl-get-photos 61_Photos_Unsorted
end
