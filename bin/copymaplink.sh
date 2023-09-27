#!/bin/bash
#copy 1
sleep 0.1
xdotool keydown Control key c key Control
sleep .$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Alt key Tab key Alt
sleep 0.1
xdotool keydown Control key t key Control
sleep .005
xdotool keydown Control key l key Control
sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Control key v key Control
sleep .$[ ( $RANDOM % 6 ) + 7 ]s
xdotool key Return
#copy 2
sleep 0.1
xdotool keydown Alt key Tab key Alt
sleep 0.1
xdotool key Down
xdotool keydown Control key c key Control
sleep .$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Alt key Tab key Alt
sleep 0.1
xdotool keydown Control key t key Control
sleep .005
xdotool keydown Control key l key Control
sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Control key v key Control
sleep .$[ ( $RANDOM % 6 ) + 7 ]s
xdotool key Return
#copy 3
sleep 0.1
xdotool keydown Alt key Tab key Alt
sleep 0.1
xdotool key Down
sleep 0.1
xdotool keydown Control key c key Control
sleep .$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Alt key Tab key Alt
sleep 0.1
xdotool keydown Control key t key Control
sleep .005
xdotool keydown Control key l key Control
sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Control key v key Control
sleep .$[ ( $RANDOM % 6 ) + 7 ]s
xdotool key Return

sleep 2
xdotool keydown Control key Tab key Control
sleep 0.1
xdotool keydown Control key Tab key Control
sleep 2

#get 1
xdotool keydown Control key l key Control
sleep .$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Control key c key Control
sleep 0.1
xdotool keydown Control key w key Control
sleep .005
xdotool keydown Alt key Tab key Alt
sleep 0.1
xdotool key Up
sleep 0.01
xdotool key Up
sleep 0.01
xdotool key Right
sleep 0.1
xdotool keydown Control key v key Control
sleep 0.5
#get 2
sleep 0.1
xdotool key Down
sleep 0.1
xdotool keydown Alt key Tab key Alt
sleep .0$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Control key l key Control
sleep 0.4
xdotool keydown Control key c key Control
sleep 0.1
xdotool keydown Control key w key Control
sleep .005
xdotool keydown Alt key Tab key Alt
sleep 0.5
xdotool keydown Control key v key Control
sleep 0.2
#get 3
xdotool key Down
sleep 0.1
xdotool keydown Alt key Tab key Alt
sleep .$[ ( $RANDOM % 6 ) + 7 ]s
xdotool keydown Control key l key Control
sleep 0.3
xdotool keydown Control key c key Control
sleep 0.1
xdotool keydown Control key w key Control
sleep .05
xdotool keydown Alt key Tab key Alt
sleep 0.3
xdotool keydown Control key v key Control
sleep 0.2
#reset pointer
xdotool key Down
xdotool key Left
