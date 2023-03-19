kde-inhibit --colorCorrect sleep 0.1
xset -r 108
xset -r 135
pkill xbindkeys && xbindkeys

sleep 3
pkill ibus
xinput set-prop 9 310 1
~/bin/trackballscroll.sh &
xmodmap -e "clear Lock" > /dev/null
