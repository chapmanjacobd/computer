Process, Priority, , H
SetWorkingDir %A_ScriptDir%
#SingleInstance force
#NoEnv
#MaxHotkeysPerInterval 120
SendMode Event
SetTitleMatchMode, 2
SetScrollLockState,Off
SetScrollLockState,AlwaysOff
SetDefaultMouseSpeed, 1
return

;;keys

CapsLock::Backspace

;make media keys work
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

;F12::Media_Next
;Media_Next::F12

;F11::Media_Prev
;Media_Prev::F10

;F10::Media_Play_Pause
;Media_Play_Pause::F11

;F9::Media_Stop
;Media_Stop::F9


$*XButton2::
Hotkey, $*XButton2 Up, XButton2up, off
;KeyWait, XButton2, T0.4
;If ErrorLevel = 1
;{
   Hotkey, $*XButton2 Up, XButton2up, on
   MouseGetPos, ox, oy
   SetTimer, WatchTheMouse, 5
   movedx := 0
   movedy := 0
   pixelsMoved := 0
;   TrayTip, Scrolling started, Emulating scroll wheel
;}
;Else
;   Send {XButton2}
return

XButton2up:
Hotkey, $*XButton2 Up, XButton2up, off
SetTimer, WatchTheMouse, off
;TrayTip
If (pixelsMoved = 0)
{
    ;The mouse was not moved, send the click event
    ; (May want to make it PGUP or something)
    Send {XButton2alt}
    Send {XButton2Up}
}
return

WatchTheMouse:
MouseGetPos, nx, ny
movedx := movedx+nx-ox
movedy := movedy+ny-oy

pixelsMoved := pixelsMoved + Abs(nx-ox) + Abs(ny-oy)

timesX := Abs(movedx) / 10
ControlGetFocus, control, A
Loop, %timesX%
{
    If (movedx > 0)
    {
        SendMessage, 0x114, 1, 0, %control%, A ; 0x114 is WM_HSCROLL
        movedx := movedx / 8
    }
    Else
    {
        SendMessage, 0x114, 0, 0, %control%, A ; 0x114 is WM_HSCROLL
        movedx := movedx / 8
    }
}

timesY := Abs(movedy) / 10
Loop, %timesY%
{
    If (movedy > 0)
    {
        Click WheelDown
        movedy := movedy / 6
    }
    Else
    {
        Click WheelUp
        movedy := movedy / 6
    }
}   

MouseMove ox, oy
return

;WheelLeft::^PgUp
;WheelRight::^PgDn
;
;RButton::Send {RButton}
;
;    RButton & WheelUp::
;    Send, {blind}{PGUP}
;    Sleep, 10
;    return
;
;    RButton & WheelDown::
;    Send, {blind}{PGDN}
;    Sleep, 10
;    return
;    
;    RButton & MButton::
;    Send, ^w
;    Sleep, 200
;    return
;    
;return

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

;;extend

;HINT: use original keys yo


;
;    #`::`
;    #1::1
;    #2::2
;    #3::3
;    #4::4
;    #5::5
;    #6::6
;    #7::7
;    #8::8
;    #9::9
;    #0::0
;    #-::-
;    #=::=
;
;    #q::Send ^{Home}
#w::Send !{F4}
#e::Run Z:\
#r::Run powershell.exe
;    #t::t
;    #y::Send {Home}
;    #u::Send {Up}
;    #i::Send {End}
;    ;#o::
;    ;#p::``
;    ;#[::
;    #]::]
;    #\::Capslock
;    
;    #a::Send ^{End}
;    #s::Send {F2}
;    #d::Send {Del}
#f:: Run C:\Program Files (x86)\Notepad++\notepad++.exe
#g:: Run http://www.google.com/search?q=%clipboard%
#^g::Run http://google.com/search?btnI=I`%27m+Feeling+Lucky&q=%clipboard%
;    #h::Send {Left}
;    #j::Send {Down}
;    #k::Send {Right}
;    #l::
;    
;    #`;::
;    
;    ;#'::MouseMove,  20,  0, 0, R
;    
#z::Run C:\bbZero\blackbox.exe -exec @bbcore.ShowMenu
;    #x::x
;    #c::LButton
;    #v::RButton
;    #b::b
;    #n::n
;    #m::m
;    ;#,::
;    ;#.::
;    ;#/::

;#IfWinActive, unsorted
;    Del::Send {Space} {Del}
;return

WinTitle:
WinActivate, %A_ThisMenuItem%
return

;mods

#If WinActive("ahk_class OpusApp") || WinActive("ahk_class XLMAIN")
    
    +^z::Send ^y
    
return

#If WinActive("ahk_exe ACDSeeUltimate10.exe")
    
    End::Send {Del}
    
return

;#If WinActive("ahk_exe explorer.exe")   
;    Enter::Send {Space} {Enter}
;return

#If WinActive("ahk_class SUMATRA_PDF_FRAME") || WinActive("ahk_class MediaPlayerClassicW")

*W::Send, !{F4}

RButton::Send {RButton}

    RButton & XButton2::
    Send, !{F4}
    Sleep, 10
    return
    
return

#If
