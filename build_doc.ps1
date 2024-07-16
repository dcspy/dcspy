$doc_dir = $args[0]
Set-Location $doc_dir
sphinx-apidoc -o ./ ../src/
make clean html
make html
