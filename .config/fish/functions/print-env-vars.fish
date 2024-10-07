# Defined interactively
function print-env-vars
    while read -l var_name
        echo "$var_name $$var_name"
    end
end
