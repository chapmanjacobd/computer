function setdefault --no-scope-shadowing
    set -q $argv[1] || set $argv[1] $argv[2..-1]
end
