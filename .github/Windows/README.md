# Setup

## Setup music

https://youtu.be/eh3SK-97Sss

## Package Manager

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

scoop bucket add extras
FOR /F %i IN (scoop_installed.txt) DO scoop install %i

clink autorun install

clink set clink.logo none
clink set clink.autostart nu
clink set history.max_lines 888888

setx path "%path%;C:\Users\JChapman\bin;C:\Users\JChapman\scoop\apps\msys2\current\usr\bin;C:\Users\JChapman\scoop\apps\msys2\current\mingw64\bin\"

code --install-extension amodio.restore-editors

setup task scheduler C:\Users\JChapman\scoop\shims\scoop.cmd update --all

msys2
xargs -a pacman_installed.txt pacman -S --needed --noconfirm

pip install pyreadline3
```

## PowerShell

```ps1
Install-Module PSEverything
Install-Module PowerTab
```

## Mouse

https://superuser.com/questions/954021/how-do-you-enable-focus-follows-mouse-in-windows-10

### Keyboard alternatives

- https://github.com/dreymar/bigbagkbdtrixpkl
- https://github.com/colemakmods/mod-dh#windows
- https://github.com/kmonad/kmonad/blob/master/doc/installation.md#windows-environment

## Misc

- https://learn.microsoft.com/en-us/windows/powertoys/run
- https://www.grc.com/wizmo/wizmo.htm

- https://ninite.com/
- https://raw.githubusercontent.com/niedzielski/cb/main/cb
- https://github.com/chapmanjacobd/computer/tree/main/.github
- https://community.chocolatey.org/packages
- https://keypirinha.com/
- https://github.com/chapmanjacobd/library/blob/main/.github/Windows.md

## Remove distractions, but only ones that have popups, obviously slow the computer, or otherwise inhibit work

- https://gist.github.com/mikepruett3/7ca6518051383ee14f9cf8ae63ba18a7
- https://github.com/Raphire/Win11Debloat
- https://github.com/Jisll/windows11/blob/main/Perfect%20Windows/Start%20Optimize%20Windows.bat
- https://github.com/Jisll/windows11/blob/main/Debloating/Remove%20Packages.cmd
- https://github.com/valinet/ExplorerPatcher
- https://github.com/Open-Shell/Open-Shell-Menu

## Alternatively...

- https://github.com/directvt/vtm
- https://github.com/cairoshell/cairoshell
- http://blackbox4windows.com/index.php?/topic/123-mojmirs-build/
- https://www.most-useful.com/kde-plasma-on-wsl.html

## Debloat

```bat
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCloudSearch /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortanaAboveLock /t REG_DWORD /d 0 /f

reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Search" /v CortanaEnabled /t REG_DWORD /d 0 /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Search" /v CortanaConsent /t REG_DWORD /d 0 /f

:: Old Context menu style
reg add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve

reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge" /v BingAdsSuppression /t REG_DWORD /d 1 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge" /v EdgeShoppingAssistantEnabled /t REG_DWORD /d 0 /f


set "RegKeyCloudContent=HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\CloudContent"
set "RegKeyPersonalization=HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Personalization"

:: Turn off Lock Screen Spotlight
reg add "%RegKeyCloudContent%" /v DisableWindowsSpotlightWindowsWelcomeExperience /t REG_DWORD /d 1 /f
reg add "%RegKeyPersonalization%" /v NoChangingLockScreen /t REG_DWORD /d 0 /f
reg add "%RegKeyCloudContent%" /v DisableWindowsSpotlightFeatures /t REG_DWORD /d 1 /f
reg add "%RegKeyCloudContent%" /v DisableWindowsSpotlightOnActionCenter /t REG_DWORD /d 1 /f
reg add "%RegKeyCloudContent%" /v DisableWindowsSpotlightOnSettings /t REG_DWORD /d 1 /f
reg add "%RegKeyCloudContent%" /v DisableThirdPartySuggestions /t REG_DWORD /d 1 /f

REG ADD "HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Explorer" /v HideRecentlyAddedApps /t REG_DWORD /d 1 /f
REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Assistance\Client\1.0" /v NoActiveHelp /t REG_DWORD /d 1 /f
REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" /v SmartScreenEnabled /t REG_SZ /d "Off" /f



:: Define Registry Keys
set "RegKeyHKCU=HKEY_CURRENT_USER\Software"
set "RegKeyHKLM=HKEY_LOCAL_MACHINE\SOFTWARE"

:: Disable Meet Now
echo Disabling Meet Now...
reg add "%RegKeyHKCU%\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v HideSCAMeetNow /t REG_DWORD /d 1 /f
reg add "%RegKeyHKLM%\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v HideSCAMeetNow /t REG_DWORD /d 1 /f

:: Disable People
echo Disabling People...
reg add "%RegKeyHKLM%\Policies\Microsoft\Windows\Explorer" /v HidePeopleBar /t REG_DWORD /d 1 /f
reg add "%RegKeyHKCU%\Policies\Microsoft\Windows\Explorer" /v HidePeopleBar /t REG_DWORD /d 1 /f

:: Hide People Bar
echo Hiding People Bar...
reg add "%RegKeyHKLM%\Microsoft\Windows\CurrentVersion\Explorer\Advanced\People" /v PeopleBand /t REG_DWORD /d 0 /f

:: Disable Weather, News, and Interests on taskbar
echo Disabling Weather, News, and Interests on taskbar...
reg add "%RegKeyHKLM%\Policies\Microsoft\Windows\Windows Feeds" /v EnableFeeds /t REG_DWORD /d 0 /f

:: Hide Weather, News, and Interests on taskbar
echo Hiding Weather, News, and Interests on taskbar...
reg add "%RegKeyHKLM%\Microsoft\Windows\CurrentVersion\Feeds" /v ShellFeedsTaskbarViewMode /t REG_DWORD /d 2 /f


reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v AllowOnlineTips /t REG_DWORD /d 0 /f

set "folders_to_hide=31C0DD25-9439-4F12-BF41-7FF4EDA38722 35286a68-3c57-41a1-bbb1-0eae73d76c95 f42ee2d3-909f-4907-8871-4c22fc0bf756 7d83ee9b-2244-4e70-b1f5-5393042af1e4 0ddd015d-b06c-45d5-8c4c-f59713854639 a0c69a99-21c8-4671-8703-7934162fcf1d B4BFCC3A-DB2C-424C-B029-7FE99A87C641"

:: Hide specified folders in This PC
for %%f in (%folders_to_hide%) do (
    reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FolderDescriptions\{%%f}\PropertyBag" /v ThisPCPolicy /t REG_SZ /d Hide /f
    reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Explorer\FolderDescriptions\{%%f}\PropertyBag" /v ThisPCPolicy /t REG_SZ /d Hide /f
)
```

## Remove animations

```bat
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v "EnableTransparency" /t REG_DWORD /d "0" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d "3" /f
reg add "HKCU\Control Panel\Desktop" /v "DragFullWindows" /t REG_SZ /d "1" /f
reg add "HKCU\Control Panel\Desktop" /v "FontSmoothingType" /t REG_DWORD /d "2" /f
reg add "HKCU\Control Panel\Desktop" /v "UserPreferencesMask" /t REG_BINARY /d "9012038010000000" /f
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /t REG_SZ /d "0" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "IconsOnly" /t REG_DWORD /d "0" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "ListviewAlphaSelect" /t REG_DWORD /d "0" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "ListviewShadow" /t REG_DWORD /d "0" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "TaskbarAnimations" /t REG_DWORD /d "0" /f
reg add "HKCU\Software\Microsoft\Windows\DWM" /v "AlwaysHibernateThumbnails" /t REG_DWORD /d "0" /f
reg add "HKCU\Software\Microsoft\Windows\DWM" /v "EnableAeroPeek" /t REG_DWORD /d "0" /f
```
