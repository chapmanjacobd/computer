# Defined interactively
function decode-url
    python -c 'from xklb.utils.web import url_decode
import sys 
for s in sys.stdin: 
    sys.stdout.write(url_decode(s))
'
end
