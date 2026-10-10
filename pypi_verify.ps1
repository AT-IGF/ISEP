$python = (Resolve-Path .\.venv-test\Scripts\python.exe).Path
$wheel = (Get-ChildItem .\dist\*.whl | Select-Object -First 1).FullName

& $python -m pip install --force-reinstall --no-deps $wheel
& $python -m pip check