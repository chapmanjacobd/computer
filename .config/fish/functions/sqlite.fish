# Defined via `source`
function sqlite --wraps=sqlite-utils --description 'alias sqlite sqlite.utils'
    sqlite.utils $argv

end
