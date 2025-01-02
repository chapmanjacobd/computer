# Defined interactively
function git_remote_use_https --description 'Update the origin remote URL to use https:// instead of git@'
    # Check if we're in a Git repository
    if not git rev-parse --git-dir >/dev/null 2>&1
        echo "Error: Not in a Git repository."
        return 1
    end

    # Get the current origin URL
    set current_url (git config --get remote.origin.url)

    # Check if the URL is in git@ format and replace it
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

    # Update the origin remote URL
    git remote set-url origin $new_url
    echo "Updated origin URL to: $new_url"
end
