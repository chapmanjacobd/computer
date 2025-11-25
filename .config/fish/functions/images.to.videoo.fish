function images.to.videoo --argument pictime crossfadetime
    while read -l line
        set listOfImages "$listOfImages" "$line" \n
    end
    set A (coalesce $pictime 7)
    set B (coalesce $crossfadetime 10)
    ffmpeg -y -pattern_type glob -i '*.jpg' -vf zoompan=d=(math $A+$B)/$B:s=1280x720:fps=1/$B,framerate=25:interp_start=0:interp_end=255:scene=100 -c:v mpeg4 -maxrate 5M -q:v 2 out.mp4
end
