# Tests for number.to.roman. Run with: fishtape ~/.config/fish/tests/number.to.roman.fish

@test "converts 1" (number.to.roman 1) = I
@test "converts 4 using subtraction" (number.to.roman 4) = IV
@test "converts 9 using subtraction" (number.to.roman 9) = IX
@test "converts 14" (number.to.roman 14) = XIV
@test "converts 40" (number.to.roman 40) = XL
@test "converts 90" (number.to.roman 90) = XC
@test "converts 400" (number.to.roman 400) = CD
@test "converts 1994" (number.to.roman 1994) = MCMXCIV
@test "converts the maximum 3999" (number.to.roman 3999) = MMMCMXCIX

@test "converts one number per stdin line" (printf '%s\n' 1 14 3999 | number.to.roman | string join '|') = 'I|XIV|MMMCMXCIX'

@test "rejects zero" (number.to.roman 0 2>/dev/null; echo $status) = 1
@test "rejects numbers above 3999" (number.to.roman 4000 2>/dev/null; echo $status) = 1
@test "rejects non-numeric input" (number.to.roman abc 2>/dev/null; echo $status) = 1
@test "reports the valid range" (number.to.roman 4000 2>&1) = 'Error: Number must be between 1 and 3999'
@test "reports non-numeric input" (number.to.roman abc 2>&1) = 'Error: Input must be a positive integer (1-3999)'
