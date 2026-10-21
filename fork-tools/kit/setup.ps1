param([Parameter(Mandatory = $true)][string]$Dump)
$ErrorActionPreference = "Stop"
$kit = $PSScriptRoot
$Dump = (Resolve-Path $Dump).Path
if (-not (Test-Path "$Dump\eboot.bin")) { throw "No eboot.bin in $Dump. Point -Dump at your own decrypted NHL 27 (PPSA34063) folder." }
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python 3 is required for unwrap_self.py. Install it from python.org and run this again." }
$src = "$kit\convert\src"
$out = "$kit\convert\out"
Remove-Item -Recurse -Force "$kit\convert" -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$src\sce_module", $out | Out-Null
Write-Output "Unwrapping eboot.bin and modules"
& $python.Source "$kit\tools\unwrap_self.py" "$Dump\eboot.bin" "$src\eboot.elf"
if ($LASTEXITCODE -ne 0) { throw "unwrap of eboot.bin failed" }
foreach ($module in Get-ChildItem "$Dump\*.prx" | Where-Object { $_.Name -notlike "*.guest.prx" }) {
    & $python.Source "$kit\tools\unwrap_self.py" $module.FullName "$src\$($module.Name)"
    if ($LASTEXITCODE -ne 0) { throw "unwrap of $($module.Name) failed" }
}
foreach ($module in Get-ChildItem "$Dump\sce_module\*.prx" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notlike "*.guest.prx" }) {
    & $python.Source "$kit\tools\unwrap_self.py" $module.FullName "$src\sce_module\$($module.Name)"
    if ($LASTEXITCODE -ne 0) { throw "unwrap of sce_module\$($module.Name) failed" }
}
Write-Output "Converting (a few minutes)"
Push-Location $src
& "$kit\tools\relinker.exe" --windows --registry --module-dir . eboot.elf "$out\eboot.exe"
$code = $LASTEXITCODE
Pop-Location
if ($code -ne 0) { throw "relinker failed with exit code $code" }
foreach ($guest in Get-ChildItem -Recurse "$out\app0\*.guest.prx") {
    $relative = $guest.FullName.Substring("$out\app0\".Length)
    Copy-Item $guest.FullName "$Dump\$relative" -Force
}
$windows = "$kit\windows"
New-Item -ItemType Directory -Force $windows | Out-Null
Copy-Item "$out\eboot.exe" $windows -Force
if (-not (Test-Path "$windows\libs")) { New-Item -ItemType Junction -Path "$windows\libs" -Target "$kit\libs" | Out-Null }
if (Test-Path "$windows\app0") { cmd /c rmdir "$windows\app0" }
New-Item -ItemType Junction -Path "$windows\app0" -Target $Dump | Out-Null
Copy-Item "$kit\Run NHL 27.cmd" $windows -Force
Write-Output "Done. Start the game with: $windows\Run NHL 27.cmd"
