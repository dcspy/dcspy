$doc_dir = $args[0]
Set-Location $doc_dir
sphinx-apidoc -o ./ ../dcpmessagepython/
make clean html
make html
