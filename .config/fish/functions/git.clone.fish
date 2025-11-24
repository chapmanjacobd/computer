# Defined via `source`
function git.clone --argument-names url

    switch $url
        case 'https://github.com/*'
            set url (string replace 'https://github.com/' 'git@github.com:' $url)
        case 'https://gitlab.com/*'
            set url (string replace 'https://gitlab.com/' 'git@gitlab.com:' $url)
        case 'https://bitbucket.org/*'
            set url (string replace 'https://bitbucket.org/' 'git@bitbucket.org:' $url)
        case 'https://codeberg.org/*'
            set url (string replace 'https://codeberg.org/' 'git@codeberg.org:' $url)
    end

    git clone $url
end
