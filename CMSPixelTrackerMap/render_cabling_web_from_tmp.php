<?php
$file = $_GET['file'];
$contenttype = $_GET['contenttype'];

$pname = $file;
$f=fopen($file,"r");
$size = filesize($file);
$data = fread($f,$size);
header("Content-type: $contenttype");
header("Content-length: $size");
header("Content-Disposition: inline; filename=$pname");
header("Content-Description: PHP Generated Data");
echo $data;
?>