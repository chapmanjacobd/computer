# Defined interactively
function knowledge
    for l in $argv
        echo $l | sed 's|\.m\.|.|' | sed 's|https://youtu.be/|https://www.youtube.com/watch?v=|' >>~/j/lists/knowledge.list
    end
    sorted ~/j/lists/knowledge.list
end
