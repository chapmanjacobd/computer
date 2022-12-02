kde-inhibit --colorCorrect sleep 0.1
sleep 5
pkill ibus
xinput set-prop 9 310 1
~/bin/trackballscroll.sh &
xmodmap -e "clear Lock" > /dev/null
