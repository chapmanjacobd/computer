# Defined interactively
function redarc.pics
    zstdcat $argv | jq -r 'select(.score > 7) | .url' | grep -iE 'tumblr.com|bdsmlr.com|ibb.co|subimg.net|imgur.com|i.redd.it|reddit.com/gallery/|artstation.com|fitnakedgirls.com|i.reddituploads.com|facebook.com/photo|facebook.com/.*/photos|facebook.com/.*/posts|vidble.com|flickr.com|minus.com|blogspot.com|twitter.com'
end
