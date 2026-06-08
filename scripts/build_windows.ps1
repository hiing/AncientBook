$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot
$IconPath = Join-Path $ProjectRoot "assets\icon\AncientBook.ico"

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
    --icon $IconPath `
    --hidden-import PySide6.QtCore `
    --hidden-import PySide6.QtGui `
    --hidden-import PySide6.QtWidgets `
    --exclude-module PySide6.QtQml `
    --exclude-module PySide6.QtQuick `
    --exclude-module PySide6.QtQuickWidgets `
    --exclude-module PySide6.QtWebEngineCore `
    --exclude-module PySide6.QtWebEngineQuick `
    --exclude-module PySide6.QtWebEngineWidgets `
    --distpath dist `
    --workpath build `
    --specpath build `
    packaging/windows_desktop.py

$ExePath = Join-Path $ProjectRoot "dist\AncientBook\AncientBook.exe"
if (-not (Test-Path $ExePath)) {
    throw "Build failed: AncientBook.exe was not created."
}

Write-Host "Build complete:"
Write-Host $ExePath
