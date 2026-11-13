$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { throw 'Run .\setup.ps1 first.' }
$taskPreviousLanHosts = $env:LUMINA_LAN_HOSTS
$taskLanHosts = @(
  foreach ($taskAdapter in [System.Net.NetworkInformation.NetworkInterface]::GetAllNetworkInterfaces()) {
    if ($taskAdapter.OperationalStatus -ne 'Up' -or $taskAdapter.NetworkInterfaceType -eq 'Loopback') { continue }
    $taskProperties = $taskAdapter.GetIPProperties()
    if (-not @($taskProperties.GatewayAddresses | Where-Object { $_.Address.AddressFamily -eq 'InterNetwork' -and $_.Address.ToString() -ne '0.0.0.0' }).Count) { continue }
    foreach ($taskUnicast in $taskProperties.UnicastAddresses) {
      $taskAddress = $taskUnicast.Address.ToString()
      if ($taskUnicast.Address.AddressFamily -eq 'InterNetwork' -and $taskAddress -match '^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)') { $taskAddress }
    }
  }
) | Select-Object -Unique
$env:LUMINA_LAN_HOSTS = $taskLanHosts -join ','
$taskShell = (Get-Process -Id $PID).Path
$taskBackend = $null
$taskFrontend = $null
try {
  $taskOccupiedPorts = @([System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() | Where-Object { $_.Port -in @(5173,8000) } | Select-Object -ExpandProperty Port -Unique)
  if ($taskOccupiedPorts.Count) {
    Write-Host 'If Lumina is already running, open http://localhost:5173'
    foreach ($taskLanHost in $taskLanHosts) { Write-Host "Phone / same Wi-Fi: http://${taskLanHost}:5173" }
    throw "Port(s) $($taskOccupiedPorts -join ', ') are already in use. Stop the original Lumina terminal with Ctrl+C before starting another copy."
  }
  $taskBackend = Start-Process -FilePath '.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000' -WindowStyle Hidden -PassThru -RedirectStandardOutput 'backend-server.log' -RedirectStandardError 'backend-error.log'
  $taskFrontend = Start-Process -FilePath $taskShell -ArgumentList '-NoProfile','-Command','npm run dev' -WindowStyle Hidden -PassThru -RedirectStandardOutput 'frontend-server.log' -RedirectStandardError 'frontend-error.log'
  Write-Host 'Lumina AI: http://localhost:5173'
  foreach ($taskLanHost in $taskLanHosts) { Write-Host "Phone / same Wi-Fi: http://${taskLanHost}:5173" }
  Write-Host 'Backend:   http://localhost:8000'
  Write-Host 'Keep this terminal open. Press Ctrl+C to stop both services.'
  while (-not $taskBackend.HasExited -and -not $taskFrontend.HasExited) { Start-Sleep -Seconds 1 }
  if ($taskBackend.HasExited) {
    Write-Host 'Backend error details:'
    Get-Content -LiteralPath 'backend-error.log' -Tail 12 -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }
  }
  if ($taskFrontend.HasExited) {
    Write-Host 'Frontend error details:'
    Get-Content -LiteralPath 'frontend-error.log' -Tail 12 -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }
  }
  throw 'A service exited. See the error details above.'
} finally {
  $env:LUMINA_LAN_HOSTS = $taskPreviousLanHosts
  foreach ($taskProcess in @($taskBackend,$taskFrontend)) {
    if ($taskProcess -and -not $taskProcess.HasExited) {
      # Stop only this launcher's process tree, including Vite's node child.
      & taskkill.exe /PID $taskProcess.Id /T /F 2>$null | Out-Null
    }
  }
}
