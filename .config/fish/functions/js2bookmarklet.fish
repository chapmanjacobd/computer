# Defined interactively
function js2bookmarklet --description 'Convert a JS file into a bookmarklet'
    set -l args $argv

    if test (count $args) -lt 1
        echo "Usage: js2bookmarklet <file.js> [output_file]" >&2
        return 1
    end

    set -l input $args[1]

    if not test -f $input
        echo "Error: File '$input' not found." >&2
        return 1
    end

    set -l minified (terser $input --compress --mangle --ecma 2020)
    if test $status -ne 0
        return 1
    end

    set -l code (printf '%s' "$minified" | node -e '
        const fs = require("fs");
        const code = fs.readFileSync(0, "utf-8").trim();
        const encoded = encodeURIComponent(code);
        console.log(`javascript:void((function(){${encoded}})());`);
    ')

    if test (count $args) -ge 2
        echo -n $code >$args[2]
        echo "Bookmarklet saved to $args[2]"
    else
        echo $code | cb
    end
end
