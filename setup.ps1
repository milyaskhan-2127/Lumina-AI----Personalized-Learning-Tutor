$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
  python -m venv .venv
  if ($LASTEXITCODE -ne 0) { throw 'Python 3.12+ is required.' }
}
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python installation failed.' }
npm install
if ($LASTEXITCODE -ne 0) { throw 'Frontend installation failed.' }
Write-Host 'Ready. Put your NVIDIA key in API.txt, then run .\start.ps1'
