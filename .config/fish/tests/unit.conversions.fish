# Tests for unit conversions. Run with: fishtape ~/.config/fish/tests/unit.conversions.fish

@test "hhmmss: 0 seconds" (hhmmss 0) = '00:00'
@test "hhmmss: 59 seconds" (hhmmss 59) = '00:59'
@test "hhmmss: 60 seconds" (hhmmss 60) = '01:00'
@test "hhmmss: 3599 seconds" (hhmmss 3599) = '59:59'
@test "hhmmss: 3600 seconds" (hhmmss 3600) = '01:00:00'
@test "hhmmss: 3661 seconds" (hhmmss 3661) = '01:01:01'
@test "hhmmss: 86399 seconds" (hhmmss 86399) = '23:59:59'
@test "hhmmss: more than one day" (hhmmss 90061) = '25:01:01'

@test "percent: one half" (percent 1 2) = 50
@test "percent: rounds to one decimal place" (percent 1 3) = 33.3
@test "percent: rounds up" (percent 2 3) = 66.7
@test "percent: rejects a zero denominator" (percent 1 0 2>/dev/null; echo $status) = 1

@test "percent.from.float: 0.5" (echo 0.5 | percent.from.float) = '50.00%'
@test "percent.from.float: 0.333" (echo 0.333 | percent.from.float) = '33.30%'
@test "percent.from.float: negative input" (echo -0.25 | percent.from.float) = '-25.00%'

@test "hours.to.seconds: whole hours" (hours.to.seconds 2) = 7200
@test "hours.to.seconds: fractional hours" (hours.to.seconds 1.5) = 5400

@test "minutes.to.seconds: whole minutes" (minutes.to.seconds 2) = 120
@test "minutes.to.seconds: fractional minutes" (minutes.to.seconds 1.5) = 90
