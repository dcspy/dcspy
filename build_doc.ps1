$doc_dir = $args[0]
$curr_dir = Get-Location
Set-Location $doc_dir
sphinx-apidoc -o .\ ..\dcspy\
.\make clean html
.\make html
Set-Location $curr_dir
