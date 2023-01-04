# Defined via `source`
function raadd --argument dfolder
    lb-dev redditadd --audio -c $dfolder --subreddits --lookback 900 -v reddit/$dfolder.db (cat ~/mc/$dfolder-reddit.txt)
end
