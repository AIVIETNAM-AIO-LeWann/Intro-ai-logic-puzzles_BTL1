param([ValidateRange(0, 65535)][int]$Port = 8765)

# Prefer an explicit interpreter, then installed Python, then Codex's runtime.
$ErrorActionPreference = 'Stop'
$candidates = @()
if ($env:PYTHON -and (Test-Path -LiteralPath $env:PYTHON -PathType Leaf)) {
    $candidates += @{ Executable = $env:PYTHON; Prefix = @() }
}
$launcher = Get-Command py -ErrorAction SilentlyContinue
if ($launcher) { $candidates += @{ Executable = $launcher.Source; Prefix = @('-3') } }
foreach ($name in @('python', 'python3')) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notlike '*\Microsoft\WindowsApps\*') {
        $candidates += @{ Executable = $command.Source; Prefix = @() }
    }
}
if ($env:USERPROFILE) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundledPython -PathType Leaf) {
        $candidates += @{ Executable = $bundledPython; Prefix = @() }
    }
}
foreach ($candidate in $candidates) {
    $executable = $candidate.Executable
    $prefixArgs = $candidate.Prefix
    try {
        & $executable @prefixArgs -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
        if ($LASTEXITCODE -ne 0) { continue }
    } catch { continue }
    Push-Location -LiteralPath $PSScriptRoot
    try {
        & $executable @prefixArgs app.py --port $Port
        exit $LASTEXITCODE
    } finally { Pop-Location }
}
throw 'Python 3.10+ not found. Install Python or set PYTHON to its executable path.'
