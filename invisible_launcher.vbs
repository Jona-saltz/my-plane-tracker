Set WshShell = CreateObject("WScript.Shell")
' Get the current folder path
currentDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
' Combine folder path with the bat file name
targetFile = currentDir & "start_bot.bat"
' Run it invisibly (The 0 means hidden)
WshShell.Run chr(34) & targetFile & chr(34), 0
Set WshShell = Nothing