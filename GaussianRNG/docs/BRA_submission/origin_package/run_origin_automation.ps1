param(
    [string]$WorkDir = "C:\OriginWork",
    [string]$Targets = "BRA-F6"
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $WorkDir "render_publication_figures_origin.py"
$donePath = Join-Path $WorkDir "origin_render_done.txt"
$errorPath = Join-Path $WorkDir "origin_render_error.txt"
$logPath = Join-Path $WorkDir "origin_render.log"
$launcherLogPath = Join-Path $WorkDir "origin_launcher.log"
$startupOgsPath = Join-Path $WorkDir "origin_startup.ogs"
$originExe = "C:\Program Files\OriginLab\Origin2026\Origin64.exe"

if (-not (Test-Path $scriptPath)) {
    throw "Missing Origin automation script: $scriptPath"
}

foreach ($path in @($donePath, $errorPath, $logPath)) {
    if (Test-Path $path) {
        Remove-Item $path -Force
    }
}
if (Test-Path $launcherLogPath) {
    Remove-Item $launcherLogPath -Force
}

function Write-LauncherLog {
    param([string]$Message)
    $line = "$(Get-Date -Format o) $Message"
    Add-Content -Path $launcherLogPath -Value $line
    Write-Output $line
}

$env:ORIGIN_TARGETS = $Targets
Write-LauncherLog "Configured ORIGIN_TARGETS=$Targets"
if (-not (Test-Path $originExe)) {
    throw "Origin executable not found: $originExe"
}

$labtalkScriptPath = $scriptPath -replace "\\", "/"
$startupOgs = @"
[Main]
string pyfile$ = "$labtalkScriptPath";
run -pyf %(pyfile$);
exit;
"@
Set-Content -Path $startupOgsPath -Value $startupOgs -Encoding ASCII
Write-LauncherLog "Wrote startup OGS: $startupOgsPath"

$ogsPathForOrigin = $startupOgsPath -replace "\\", "/"
$originArgs = @(
    "-h",
    "-rs",
    "run.section(`"$ogsPathForOrigin`", main)"
)
Write-LauncherLog "Starting Origin executable"
$process = Start-Process -FilePath $originExe -ArgumentList $originArgs -Wait -PassThru -NoNewWindow
Write-LauncherLog "Origin exited with code $($process.ExitCode)"

$timeoutAt = (Get-Date).AddMinutes(2)
while ((Get-Date) -lt $timeoutAt) {
    if (Test-Path $donePath) {
        Write-LauncherLog "Origin render completed."
        break
    }
    if (Test-Path $errorPath) {
        Write-LauncherLog "Origin render failed."
        Get-Content $errorPath
        throw "Origin render script reported an error."
    }
    Start-Sleep -Seconds 2
}

if (-not (Test-Path $donePath)) {
    throw "Origin finished but the render sentinel was not created."
}

if (Test-Path $logPath) {
    Get-Content $logPath
}
