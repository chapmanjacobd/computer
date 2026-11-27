# Tests for enumerate. Run with: fishtape ~/.config/fish/tests/enumerate.fish

function enumerate_test_output
    enumerate $argv | string replace -- \t : | string join '|'
end

@test "numbers arguments from one" (enumerate_test_output a b c) = '1:a|2:b|3:c'
@test "keeps spaces inside an argument" (enumerate_test_output 'a b') = '1:a b'
@test "prints nothing without arguments" -z (enumerate_test_output)
