$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

Write-Host "Installing AncientBook development dependencies..."
python -m pip install -e ".[dev]"

Write-Host "Removing previous build artifacts..."
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist\AncientBook") {
    Remove-Item -Recurse -Force "dist\AncientBook"
}

Write-Host "Building AncientBook desktop app with PyInstaller..."
python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name AncientBook `
    --collect-all PySide6 `
    --distpath dist `
    --workpath build `
    --specpath build `
    -m ancientbook.desktop.app

$ExePath = Join-Path $ProjectRoot "dist\AncientBook\AncientBook.exe"
if (-not (Test-Path $ExePath)) {
    throw "Build failed: AncientBook.exe was not created."
}

Write-Host "Build complete:"
Write-Host $ExePath
