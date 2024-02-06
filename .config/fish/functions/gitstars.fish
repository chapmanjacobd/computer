# Defined interactively
function gitstars
    for lang in rust c lua shell python c%2B%2B c%23
        firefox --new-tab $argv?language=$lang&tab=stars
    end
end
