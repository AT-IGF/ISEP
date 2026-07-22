param(
    [switch]$Console
)

$ErrorActionPreference = "Stop"

$ENV_NAME = "myenv"
$OUTPUT_DIR = "dist"
$APP_NAME = "ISEP"

# Activate conda environment
Write-Host "Activating conda environment..." -ForegroundColor Cyan
conda activate $ENV_NAME

# Pack conda environment
Write-Host "Packing conda environment..." -ForegroundColor Cyan
conda pack -n $ENV_NAME -o python_env.tar.gz --force

# Create distribution folder
Write-Host "Creating distribution folder..." -ForegroundColor Cyan
if (Test-Path $OUTPUT_DIR) { Remove-Item $OUTPUT_DIR -Recurse -Force }
New-Item -ItemType Directory -Path "$OUTPUT_DIR\python" | Out-Null

# Extract environment
Write-Host "Extracting environment..." -ForegroundColor Cyan
tar -xzf python_env.tar.gz -C "$OUTPUT_DIR\python"

# Trim unnecessary files from environment
Write-Host "Trimming environment..." -ForegroundColor Cyan
$junk = @(
    "$OUTPUT_DIR\python\Lib\site-packages\*\tests",
    "$OUTPUT_DIR\python\Lib\site-packages\*\test",
    "$OUTPUT_DIR\python\Lib\test",
    "$OUTPUT_DIR\python\Lib\unittest\test",
    "$OUTPUT_DIR\python\Lib\idlelib",
    "$OUTPUT_DIR\python\Lib\tkinter",
    "$OUTPUT_DIR\python\share",
    "$OUTPUT_DIR\python\include",
    "$OUTPUT_DIR\python\Tools",
    "$OUTPUT_DIR\python\Lib\site-packages\pip",
    "$OUTPUT_DIR\python\Lib\site-packages\setuptools",
    "$OUTPUT_DIR\python\Lib\site-packages\tensorboard"
)
foreach ($path in $junk) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Show size after trim
$size = (Get-ChildItem "$OUTPUT_DIR\python" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Environment size after trim: $([math]::Round($size)) MB" -ForegroundColor Yellow

# Copy project files
Write-Host "Copying project files..." -ForegroundColor Cyan
xcopy /E /I src "$OUTPUT_DIR\src" /Q
xcopy /E /I resources "$OUTPUT_DIR\resources" /Q

# Build exe launcher
$consoleMode = if ($Console) { "debug (with console)" } else { "release (no console)" }
Write-Host "Building exe launcher ($consoleMode)..." -ForegroundColor Cyan
$pythonExe = if ($Console) { "python.exe" } else { "pythonw.exe" }
$launcherCode = @"
using System;
using System.Diagnostics;
using System.IO;

class Launcher {
    static void Main() {
        string dir = AppDomain.CurrentDomain.BaseDirectory;
        ProcessStartInfo psi = new ProcessStartInfo();
        psi.FileName = Path.Combine(dir, "python", "$pythonExe");
        psi.Arguments = "-m src.ui.UI";
        psi.WorkingDirectory = dir;
        psi.UseShellExecute = true;
        Process p = Process.Start(psi);
        p.WaitForExit();
    }
}
"@

$launcherPath = "$OUTPUT_DIR\$APP_NAME.cs"
$launcherCode | Out-File -Encoding UTF8 $launcherPath

# Find csc.exe from .NET Framework
$csc = Join-Path $env:WINDIR "Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $csc)) {
    $csc = Join-Path $env:WINDIR "Microsoft.NET\Framework\v4.0.30319\csc.exe"
}

$target = if ($Console) { "exe" } else { "winexe" }
$iconPath = "resources\ui\icons\app.ico"
$iconFlag = if (Test-Path $iconPath) { "/win32icon:$iconPath" } else { "" }
& $csc /target:$target $iconFlag /out:"$OUTPUT_DIR\$APP_NAME.exe" $launcherPath | Out-Null
Remove-Item $launcherPath

# Cleanup
Remove-Item python_env.tar.gz -Force

$totalSize = (Get-ChildItem "$OUTPUT_DIR" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Done! Total distribution size: $([math]::Round($totalSize)) MB" -ForegroundColor Green
Write-Host "Distribution in: $OUTPUT_DIR\" -ForegroundColor Green
