param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$BuildScript = Join-Path $ProjectRoot "scripts\build_windows.ps1"
$DistDir = Join-Path $ProjectRoot "dist\AncientBook"
$ExePath = Join-Path $DistDir "AncientBook.exe"
$ReleaseRoot = Join-Path $ProjectRoot "release"
$PackageName = "AncientBook-Windows"
$PackageDir = Join-Path $ReleaseRoot $PackageName
$ZipPath = Join-Path $ReleaseRoot "AncientBook-Windows.zip"
$ReleaseReadme = Join-Path $ProjectRoot "docs\release-checklists\windows-release-readme.txt"

if (-not $SkipBuild) {
    Write-Host "Building AncientBook before packaging..."
    powershell -ExecutionPolicy Bypass -File $BuildScript
}

if (-not (Test-Path $ExePath)) {
    throw "AncientBook.exe was not found. Run scripts\build_windows.ps1 first, or run this script without -SkipBuild."
}

Write-Host "Preparing release folder..."
if (Test-Path $PackageDir) {
    Remove-Item -Recurse -Force $PackageDir
}
New-Item -ItemType Directory -Force $PackageDir | Out-Null
New-Item -ItemType Directory -Force (Join-Path $PackageDir "examples") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $PackageDir "licenses") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $PackageDir "docs") | Out-Null

Get-ChildItem -LiteralPath $DistDir -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $PackageDir -Recurse -Force
}

Copy-Item -Path (Join-Path $ProjectRoot "README.md") -Destination (Join-Path $PackageDir "README-project.md") -Force
Copy-Item -Path (Join-Path $ProjectRoot "README.en.md") -Destination (Join-Path $PackageDir "README.en.md") -Force
Copy-Item -Path (Join-Path $ProjectRoot "LICENSE") -Destination (Join-Path $PackageDir "LICENSE") -Force
Copy-Item -Path $ReleaseReadme -Destination (Join-Path $PackageDir "README-FIRST.txt") -Force
Copy-Item -Path (Join-Path $ProjectRoot "examples\sample.txt") -Destination (Join-Path $PackageDir "examples\sample.txt") -Force
Copy-Item -Path (Join-Path $ProjectRoot "docs\licenses\THIRD_PARTY_NOTICES.md") -Destination (Join-Path $PackageDir "licenses\THIRD_PARTY_NOTICES.md") -Force
Copy-Item -Path (Join-Path $ProjectRoot "docs\release-checklists\non-programmer-acceptance.md") -Destination (Join-Path $PackageDir "docs\non-programmer-acceptance.md") -Force

$VersionText = @(
    "AncientBook Windows package",
    "Generated at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')",
    "Entry point: AncientBook.exe",
    "Fonts: installed system fonts or user-selected local font files only"
)
Set-Content -Path (Join-Path $PackageDir "VERSION.txt") -Value $VersionText -Encoding UTF8

if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath
}

Write-Host "Creating release zip..."
Compress-Archive -Path $PackageDir -DestinationPath $ZipPath -Force

Write-Host "Release package complete:"
Write-Host $ZipPath
