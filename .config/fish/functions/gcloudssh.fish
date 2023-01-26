# Defined interactively
function gcloudssh
    echo 'echo "TOOLBOX_DOCKER_IMAGE=fedora" > "${HOME}/.toolboxrc"'
    echo 'echo "TOOLBOX_DOCKER_TAG=latest" >> "${HOME}/.toolboxrc"'
    echo toolbox
end
