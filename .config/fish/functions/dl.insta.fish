# Defined interactively
function dl.insta
    #with_backoff.sh 
    gdl https://www.instagram.com/$argv/
    echo $argv >>~/mc/61_Photos_Unsorted-instagram.txt
end
