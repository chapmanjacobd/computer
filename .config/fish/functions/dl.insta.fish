# Defined interactively
function dl.insta
    #with.backoff 
    dl.images https://www.instagram.com/$argv/
    echo $argv >>~/mc/61_Photos_Unsorted-instagram.txt
end
