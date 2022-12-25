# Defined interactively
function reddit --argument subr
    if grep -qEix $subr ~/github/xk/curati/61_Photos_Unsorted-reddit.txt
        return 1
    end

    echo $subr >>~/github/xk/curati/61_Photos_Unsorted-reddit.txt
    cd ~/d/61_Photos_Unsorted/
    python -m bdfr download bdfr/ -S top --subreddit $argv
    python -m bdfr download bdfr/ -S top -t month -L 400 --subreddit $argv
    python -m bdfr download bdfr/ -S top -t year --subreddit $argv

end
