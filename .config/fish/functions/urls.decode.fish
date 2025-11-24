# Defined interactively
function urls.decode
    python -c 'from library.utils.web import url_decode
from library.utils.arg_utils import stdarg
for s in stdarg():
    print(url_decode(s))
' $argv
end
