#NoEnv
#SingleInstance force
SendMode Input
SetWorkingDir %A_ScriptDir%
#MaxHotkeysPerInterval 120
Process, Priority, , H
SetTitleMatchMode 3
#installkeybdhook
SetNumLockState,On
SetNumLockState,AlwaysOn
SetScrollLockState,Off
SetScrollLockState,AlwaysOff
SetDefaultMouseSpeed, 1
return

CapsLock::Backspace
Volume_Up::
    soundset, +1
return
Volume_Down::
    soundset, -1
return
+Volume_Up::
    soundset, +20
return
+Volume_Down::
    soundset, -20
return
Volume_Mute::
    SoundSet, +1, , mute
return
F12::Media_Next
Media_Next::F12
F11::Media_Prev
F10::Media_Play_Pause
AppsKey:: return
AppsKey & Volume_Up::
    Send, ^!+{F8}
    sleep, 80
    Send, ^!+{F8}
    sleep, 80
    Send, ^!+{F8}
return
AppsKey & Volume_Down::
    Send, ^!+{F7}
    sleep, 80
    Send, ^!+{F7}
    sleep, 80
    Send, ^!+{F7}
    sleep, 80
    Send, ^!+{F7}
return

e::f
r::p
t::b
y::j
u::l
i::u
o::y
p::`;
s::r
d::s
f::t
g::g
h::m
j::n
k::e
l::i
`;::o
z::x
x::c
c::d
b::z
n::k
m::h

RButton::Send {RButton}
RButton & XButton2::
    Send, ^w
    Sleep, 10
return
RButton & XButton1::
    Send, {PGUP}
    Sleep, 20
return
RButton & LButton::
    Send, {PGDN}
    Sleep, 20
return
RButton & MButton::
    Send, ^w
    Sleep, 200
return
RButton & WheelUp::
    Send, {PGUP}
    Sleep, 10
return
RButton & WheelDown::
    Send, {PGDN}
    Sleep, 10
return
return
SetKeyDelay 30,50
XButton2alt:
XButton2 & XButton1::
    Send, ^{PGUP}
    Sleep, 10
return
XButton2 & RButton::
return
XButton2 & LButton::
    Send, ^{PGDN}
    Sleep, 10
return
return
XButton1::Send {MButton}
XButton1 & XButton2::
    soundset, +5
return
XButton1 & LButton::
return
XButton1 & RButton::
    soundset, -5
return
return

^q::Send, !{F4}

#If, GetKeyState("Lalt", "P")
    ; *`::`
    ; *1::1
    ; *2::2
    ; *3::3
    ; *4::4
    ; *5::5
    ; *6::6
    ; *7::7
    ; *8::8
    ; *9::9
    ; *0::0
    ; *-::-
    ; *=::=
    *q::Send ^{Home}
    *w::Send ^{End}
    ; *e::e
    ; *r::r
    ; *t::t
    *y::Send {Home}
    *u::Send {Up}
    *i::Send {End}
    ; *o::MouseMove, -15,-20, 0, R
    ; *p::MouseMove, 0,-20, 0, R
    ; *[::MouseMove, 15,-20, 0, R
    *]::]
    *\::Capslock
    ; *a::a
    *s::Send {F2}
    *d::Send {Del}
    ; *f::f
    ; *g::g
    *h::Send {Left}
    *j::Send {Down}
    *k::Send {Right}
    ; *l::MouseMove, -20, 0, 0, R
    ; *`;::
    ;     CoordMode, Mouse, Screen
    ;     MouseMove, (A_ScreenWidth // 2), (A_ScreenHeight // 2)
    ; return
    ; *'::MouseMove, 20, 0, 0, R
    ; *z::Send, !{F4}
    ; *x::x
    *c::LButton
    *v::RButton
    ; *n::n
    ; *m::m
    *Space::Send {Return}
    ; *+`::`
    ; *+1::1
    ; *+2::2
    ; *+3::3
    ; *+4::4
    ; *+5::5
    ; *+6::6
    ; *+7::7
    ; *+8::8
    ; *+9::9
    ; *+0::0
    ; *+-::-
    ; *+=::=
    *+q::Send {Blind}{PgUp}
    *+w::Send {Blind}{PgDn}
    ; *+e::e
    ; *+r::r
    ; *+t::t
    *+y::Send ^{Home}
    *+u::Send {Alt Down}+{Up}{Alt Up}
    *+i::Send ^{End}
    ; *+o::MouseMove, -215,-220, 0, R
    ; *+p::MouseMove, 0,-220, 0, R
    ; *+[::MouseMove, 215,-220, 0, R
    ; *+]::]
    ; *+\::\
    ; *+a::a
    *+s::Send {F2}
    *+d::Send {Blind}{Del}
    ; *+f::f
    ; *+g::g
    *+h::Send {Alt Down}+{Left}{Alt Up}
    *+j::Send {Alt Down}+{Down}{Alt Up}
    *+k::Send {Alt Down}+{Right}{Alt Up}
    ; *+l::MouseMove, -220, 0, 0, R
    ; *+`;::
    ;     CoordMode, Mouse, Screen
    ;     MouseMove, (A_ScreenWidth // 4), (A_ScreenHeight // 4)
    ; return
    ; *+'::MouseMove, 220, 0, 0, R
    ; *+z::Send, !{F4}
    ; *+x::x
    ; *+c::c
    ; *+v::v
    ; *+n::n
    ; *+m::m
    *+Space::Send {Return}
return

#If WinActive("ahk_class OpusApp") || WinActive("ahk_class XLMAIN")
    +^z::Send ^y
return
#If WinActive("ahk_class SUMATRA_PDF_FRAME") || WinActive("ahk_class MediaPlayerClassicW")
    RButton::Send {RButton}
    RButton & XButton2::
        Send, !{F4}
        Sleep, 10
    return
return

^+Space::
    WinGet, activeHwnd, ID, A

    ; Toggle the maximization state of the active window
    WinGet, MaxState, MinMax, ahk_id %activeHwnd%
    if (MaxState = 1)  ; currently maximized
        WinRestore, ahk_id %activeHwnd%
    else
        WinMaximize, ahk_id %activeHwnd%
return

#If, GetKeyState("LWin", "P")
    *f::
        WinGet, activeHwnd, ID, A
        WinSet, AlwaysOnTop, , ahk_id %activeHwnd%
    Return
Return
