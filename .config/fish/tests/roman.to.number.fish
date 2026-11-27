# Tests for roman.to.number. Run with: fishtape ~/.config/fish/tests/roman.to.number.fish

function roman_test_roundtrip
    for n in 1 4 9 14 40 90 400 1994 3999
        roman.to.number (number.to.roman $n)
    end | string join '|'
end

@test "converts I" (roman.to.number I) = 1
@test "converts V" (roman.to.number V) = 5
@test "converts X" (roman.to.number X) = 10
@test "converts L" (roman.to.number L) = 50
@test "converts C" (roman.to.number C) = 100
@test "converts D" (roman.to.number D) = 500
@test "converts M" (roman.to.number M) = 1000
@test "converts XIV" (roman.to.number XIV) = 14
@test "converts MCMXCIV" (roman.to.number MCMXCIV) = 1994
@test "converts the maximum 3999" (roman.to.number MMMCMXCIX) = 3999
@test "accepts lowercase input" (roman.to.number mcmxciv) = 1994

@test "converts one numeral per stdin line" (printf '%s\n' I XIV MCMXCIV | roman.to.number | string join '|') = '1|14|1994'
@test "round-trips representative values" (roman_test_roundtrip) = '1|4|9|14|40|90|400|1994|3999'

@test "rejects letters outside the Roman set" (roman.to.number ABC 2>/dev/null; echo $status) = 1
@test "reports invalid input" (roman.to.number ABC 2>&1) = 'Error: Input must be a valid Roman numeral (I, V, X, L, C, D, M)'
