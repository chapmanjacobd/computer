function slideshowFill --argument seconds
    while read -l line
        set listOfImages "$listOfImages" "$line" \n
    end
    set listCount (string join \n $listOfImages | wc -l)
    set timePerImage (math "$seconds/$listCount")
    set pictime (math "$timePerImage*0.6")
    set crossfadetime (math "$timePerImage*0.4")
    echo "$listOfImages" $pictime $crossfadetime
end
