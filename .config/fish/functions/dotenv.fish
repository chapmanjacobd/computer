# Defined interactively
function dotenv
    env -S (cat .env) $argv
end
