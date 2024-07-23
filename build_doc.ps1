$doc_dir = $args[0]
Set-Location $doc_dir
sphinx-apidoc -o ./ ../dcspy/
make clean html
make html
