$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { throw 'Run .\setup.ps1 first.' }
$taskShell = (Get-Process -Id $PID).Path
$taskBackend = $null
$taskFrontend = $null
try {
  $taskBackend = Start-Process -FilePath '.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000' -WindowStyle Hidden -PassThru -RedirectStandardOutput 'backend-server.log' -RedirectStandardError 'backend-error.log'
  $taskFrontend = Start-Process -FilePath $taskShell -ArgumentList '-NoProfile','-Command','npm run dev' -WindowStyle Hidden -PassThru -RedirectStandardOutput 'frontend-server.log' -RedirectStandardError 'frontend-error.log'
  Write-Host 'Lumina AI: http://localhost:5173'
  Write-Host 'Backend:   http://localhost:8000'
  Write-Host 'Keep this terminal open. Press Ctrl+C to stop both services.'
  while (-not $taskBackend.HasExited -and -not $taskFrontend.HasExited) { Start-Sleep -Seconds 1 }
  throw 'A service exited. Check the *-error.log files in this folder.'
} finally {
  foreach ($taskProcess in @($taskBackend,$taskFrontend)) {
    if ($taskProcess -and -not $taskProcess.HasExited) {
      # Stop only this launcher's process tree, including Vite's node child.
      & taskkill.exe /PID $taskProcess.Id /T /F 2>$null | Out-Null
    }
  }
}
