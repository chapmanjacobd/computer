# Defined via `source`
function gitstars
    for lang in rust c lua shell python c%2B%2B c%23 markdown html
        firefox --new-tab $argv?language=$lang&tab=stars
    end
end
