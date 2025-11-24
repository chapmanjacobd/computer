# Defined interactively
function git.remote.ssh
    if not git rev-parse --git-dir >/dev/null 2>&1
        echo "Error: Not in a Git repository."
        return 1
    end

    set current_url (git config --get remote.origin.url)

    switch $current_url
        case 'https://github.com/*'
            set new_url (string replace 'https://github.com/' 'git@github.com:' $current_url)
        case 'https://gitlab.com/*'
            set new_url (string replace 'https://gitlab.com/' 'git@gitlab.com:' $current_url)
        case 'https://bitbucket.org/*'
            set new_url (string replace 'https://bitbucket.org/' 'git@bitbucket.org:' $current_url)
        case '*'
            echo "The origin URL is already in the correct format or is not supported."
            return 0
    end

    git remote set-url origin $new_url
    git remote -v
end
