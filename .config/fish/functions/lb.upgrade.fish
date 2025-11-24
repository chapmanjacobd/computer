# Defined via `source`
function lb.upgrade
    servers.ssh pip install --upgrade library
end
