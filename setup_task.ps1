# Windows Task Scheduler registration script for Daily Bible Quotes at 7:00 AM & 10:00 PM
$taskName = "DailyBibleQuote7AM_10PM"
$pythonPath = (Get-Command python.exe).Source
$scriptPath = "$PSScriptRoot\send_bible_quote.py"

Write-Host "Registering Windows Scheduled Task '$taskName' to run daily at 7:00 AM and 10:00 PM..." -ForegroundColor Cyan

# Remove old tasks if exist
Unregister-ScheduledTask -TaskName "DailyBibleQuote7AM" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`"" -WorkingDirectory $PSScriptRoot

# Create two daily triggers: 7:00 AM and 10:00 PM
$triggerMorning = New-ScheduledTaskTrigger -Daily -At 7:00AM
$triggerNight = New-ScheduledTaskTrigger -Daily -At 10:00PM

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($triggerMorning, $triggerNight) -Settings $settings -Force

Write-Host "Task '$taskName' successfully registered!" -ForegroundColor Green
Write-Host "Triggers: Every day at 7:00 AM and 10:00 PM (sharp) with WakeToRun enabled" -ForegroundColor Green
