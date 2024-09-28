#SingleInstance, Force
#MaxThreadsPerHotkey, 2
Return ;<-- forced end of autoexecute section

RandWheel(Direction) {
    Random, Rwheel, 2, 9
    Loop, %Rwheel% {
        if(Direction)
            Send, {WheelUp}
        else
            Send, {WheelDown}
        Sleep, 40
    }
    Return
}

+Delete::
    Notifications := !Notifications
    If (!Notifications) {
       ToolTip "Notifications are disabled"
       Sleep, 800
       ToolTip
       Return
    } else {
        ToolTip "Notifications are enabled"
        Sleep, 800
        ToolTip
    }

    While (Notifications)
    {
        Random, Rtask, 0, 4
        Switch Rtask {
            Case 4:
                Random, Rdirection, 0, 1
                RandWheel(Rdirection)
                Random, Rsleep, 600, 1600
                Sleep, Rsleep
                RandWheel(!RD)
            Case 3:
                Send, {LWin}
                Random, Rsleep, 400, 2700
                Sleep, Rsleep
                Send, {LWin}
            Case 2:
                Random, Rtabbing, 1, 3
                Send, {Alt Down}
                Loop, %Rtabbing% {
                    Send, {Tab}
                    Random, Rsleep, 80, 400
                    Sleep, Rsleep
                }
                Send, {Alt Up}
            Case 1:
            Default:
                Random, Rxoffset, -400, 600
                Random, Ryoffset, -150, 300
                MouseMove, Rxoffset, Ryoffset, Mod(Rxoffset+Ryoffset, 100)
        }
        Random, Rsleep, 2000, 8000
        Sleep, Rsleep

        Sleep, 1000
    }
    Return
