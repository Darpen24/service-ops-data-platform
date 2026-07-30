[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python 3.12 is required but the python command was not found.'
}

$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($pythonVersion -ne '3.12') {
    throw "Python 3.12 is required; detected Python $pythonVersion. Install Python 3.12 and retry."
}

python --version
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e '.[dev]'

if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
    Write-Host 'Created .env from .env.example. Replace the local-development password before sharing it.'
}

Write-Host 'Setup complete. Run .\scripts\check.ps1 for Phase 0 checks.'
