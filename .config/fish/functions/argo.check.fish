# Defined interactively
function argo.check
    for w in $argv
        if argo get $w | grep -i Succeeded
            echo $w
        end
    end
end
