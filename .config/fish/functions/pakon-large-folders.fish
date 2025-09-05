# Defined interactively
function pakon-large-folders
    for db in ~/lb/fs/d*.db

        lb du $db --parents -D=-7 --folder-size=+500G
    end
end
