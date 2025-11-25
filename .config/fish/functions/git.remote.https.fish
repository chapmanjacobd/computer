# Defined via `source`
function git.remote.https --description 'Update the origin remote URL to use https:// instead of git@'
    if not git rev-parse --git-dir >/dev/null 2>&1
        echo "Error: Not in a Git repository."
        return 1
    end

    set current_url (git config --get remote.origin.url)

    switch $current_url
        case 'git@github.com:*'
            set new_url (string replace 'git@github.com:' 'https://github.com/' $current_url)
        case 'git@gitlab.com:*'
            set new_url (string replace 'git@gitlab.com:' 'https://gitlab.com/' $current_url)
        case 'git@bitbucket.org:*'
            set new_url (string replace 'git@bitbucket.org:' 'https://bitbucket.org/' $current_url)
        case '*'
            echo "The origin URL is already in the correct format or is not supported."
            return 0
    end

    git remote set-url origin $new_url
    git remote -v
end
