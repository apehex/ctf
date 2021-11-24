<?php
   
echo $ebookdownloadurl = ( isset( $_GET['ebookdownloadurl'] ) ) ? $_GET['ebookdownloadurl']: '';
echo $ebookdownloadurl = htmlspecialchars($ebookdownloadurl);
echo $ebookdownloadurl = strip_tags($ebookdownloadurl);
if($ebookdownloadurl){   
$path = parse_url($ebookdownloadurl, PHP_URL_PATH);  
$file_name = basename($path); 

header('Content-Type: application/octet-stream');
header("Content-Transfer-Encoding: Binary"); 
header("Content-disposition: attachment; filename=\"".$file_name."\""); 
readfile($ebookdownloadurl);
}
echo '<script>window.close()</script>';
exit;

?>
<script>window.close()</script>
