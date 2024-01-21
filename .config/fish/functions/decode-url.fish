# Defined interactively
function decode-url
    python -c 'from xklb.utils.web import url_decode
from xklb.utils.arg_utils import stdarg
for s in stdarg():
    print(url_decode(s))
' $argv
end
