param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$Output,
    [string]$Browser = 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    [string]$PaliMap,
    [switch]$LegacyLayout
)
$ErrorActionPreference = 'Stop'
$stylePath = if ($LegacyLayout) { "$PSScriptRoot/suttaflow.css" } else { "$PSScriptRoot/polski-pali-v2.css" }
$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$outputPath = [IO.Path]::GetFullPath($Output)
if ([IO.Path]::GetExtension($sourcePath) -ne '.md') { throw 'Wymagane źródło .md' }
if (Test-Path -LiteralPath $outputPath) { throw 'Zachowaj poprzedni PDF; wskaż nową nazwę wyjścia.' }
if (!(Test-Path -LiteralPath (Split-Path -Parent $outputPath))) { throw 'Katalog wyjściowy musi istnieć.' }
$htmlPath = [IO.Path]::ChangeExtension($outputPath, '.html')
if (Test-Path -LiteralPath $htmlPath) { throw 'Plik HTML już istnieje; wskaż nową nazwę.' }
$parallelPins = @()
if ($PaliMap) {
    if ($LegacyLayout) { throw 'PaliMap wymaga aktualnego składu polsko-palijskiego.' }
    $mapPath = (Resolve-Path -LiteralPath $PaliMap).Path
    $translationPath = $sourcePath
    $sourcePath = [IO.Path]::ChangeExtension($outputPath, '.md')
    & python -m sfe.parallel_text $translationPath $mapPath $sourcePath
    if ($LASTEXITCODE -ne 0) { throw 'Nieprawidłowa mapa PL-Pali; skład zatrzymany.' }
    $parallelPins = @($translationPath, $mapPath)
    $mapData = Get-Content -LiteralPath $mapPath -Raw | ConvertFrom-Json
    $parallelPins += (Resolve-Path -LiteralPath $mapData.source.path).Path
}
& node "$PSScriptRoot/convert.mjs" $sourcePath $htmlPath
if ($LASTEXITCODE -ne 0) { throw 'Konwersja VFM nie powiodła się.' }
& vivliostyle.cmd build $htmlPath --style $stylePath --size A4 --output $outputPath --executable-browser $Browser --timeout 90 --no-vite-config-file
if ($LASTEXITCODE -ne 0) { throw "Vivliostyle zakończył pracę z kodem $LASTEXITCODE" }
$pins = @{}
foreach ($file in @($sourcePath, $htmlPath, $outputPath, "$PSScriptRoot/suttaflow.css", "$PSScriptRoot/odstepy-r4.css", "$PSScriptRoot/polski-pali.css", $stylePath) + $parallelPins + @(Get-ChildItem -LiteralPath "$PSScriptRoot/fonts" -File | ForEach-Object FullName)) {
    $pins[$file] = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
}
$manifest = @{ status='BUILT_REQUIRES_TECHNICAL_AND_VISUAL_CHECKS'; source=$sourcePath; pdf=$outputPath; html=$htmlPath; stylesheet=$stylePath; hashes=$pins; publication_approved=$false }
if ($PaliMap) { $manifest.pali_map = $mapPath; $manifest.translation_source = $translationPath }
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath ([IO.Path]::ChangeExtension($outputPath, '.build.json')) -Encoding utf8
Write-Host "Zbudowano PDF: $outputPath. Wymagane kontrole techniczne i oględziny."
