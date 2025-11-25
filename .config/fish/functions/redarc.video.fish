# Defined interactively
function redarc.video
    zstdcat $argv | jq -r 'select(.score > 7) | .url' | grep -iE 'spankbang.com|xhamster.com|xnxx.com|xvideos.com|pbs.org|tiktok.com|npr.org|dailymotion.com|archive.org|redtube.com|ruleporn.com|youtube.com|youtu.be|youporn.com|pornhub.com|v.redd.it|zenra.net|facebook.com/video|facebook.com/.*/videos|vimeo.com|streamable.com|erome.com'
end
