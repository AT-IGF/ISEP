$ErrorActionPreference = "Stop"

Remove-Item .\dist, .\build -Recurse -Force -ErrorAction SilentlyContinue

py -3.11 -m build
if ($LASTEXITCODE -ne 0) { throw "Build failed" }

py -3.11 -m twine check --strict .\dist\*
if ($LASTEXITCODE -ne 0) { throw "Validation failed" }

Get-ChildItem .\dist

$wheel = (Get-ChildItem .\dist\*.whl | Select-Object -First 1).FullName

py -3.11 -m zipfile -l $wheel