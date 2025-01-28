$paths = @("dist", "build", "*.egg-info")
foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Output "Removing $path"
        Remove-Item -Recurse -Force $path
    }
}
python setup.py sdist
