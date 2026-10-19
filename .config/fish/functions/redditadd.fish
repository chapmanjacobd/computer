# Defined interactively
function redditadd --argument reddit_db
    lb database add reddit --subreddits -v $reddit_db $argv[2..-1]
end
