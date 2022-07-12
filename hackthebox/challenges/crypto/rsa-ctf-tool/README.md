> Crypto is fun ;)

> Author: **[r4j][author-profile]**

## Finding the weakness

The archive contains 3 files:

```shell
ls -lah sources/
# 1049409 4.0K -rw-r--r-- 1 gully gully   33 Nov 12  2019 flag.txt.aes
# 1049407 4.0K -rw-r--r-- 1 gully gully  384 Nov 12  2019 key
# 1049408 4.0K -rw-r--r-- 1 gully gully  356 Nov 12  2019 pubkey.pem
xxd sources/flag.txt.aes 
# 00000000: 4845 da30 14a5 2429 e914 c311 7b1c 45a0  HE.0..$)....{.E.
# 00000010: a68d 6454 e830 57af 6fca dada e011 814d  ..dT.0W.o......M
# 00000020: 0a
cat sources/key
# 13822f9028b100e2b345a1ad989d9cdedbacc3c706c9454ec7d63abb15b58bef8ba545bb0a3b883f91bf12ca12437eb42e26eff38d0bf4f31cf1ca21c080f11877a7bb5fa8ea97170c932226eab4812c821d082030100030d84ebc63fd8767cde994e0bd1a1f905c27fb0d7adb55e3a1f101d8b5b997ba6b1c09a5e1cc65a9206906ef5e01f13d7beeebdf389610fb54676f76ec0afc51a304403d44bb3c739fd8276f0895c3587a710d15e43fc67284070519e6e0810caf86b134f02ec54018
openssl rsa -inform PEM -text -noout -pubin -in sources/pubkey.pem
# RSA Public-Key: (1535 bit)
# Modulus:
#     77:d1:e3:2b:fe:41:fb:07:61:2b:cb:95:2e:8b:19:
#     6d:9c:30:39:41:dd:19:47:d4:fb:5e:0f:b8:0d:ea:
#     75:38:2a:1c:8c:95:1c:e7:39:44:08:ed:c8:01:d3:
#     cd:9b:b4:c5:ac:d6:eb:0f:61:f5:12:ae:a9:03:b3:
#     ed:44:0e:bc:f3:c3:8d:8c:1b:af:37:62:f2:e5:25:
#     17:dc:3b:6b:32:73:e6:0d:25:30:ea:b5:51:d6:e5:
#     5d:d2:34:9d:89:f9:62:82:c3:40:39:f9:a6:f6:a8:
#     0f:ac:7e:14:45:86:f3:c9:ee:0b:0b:bd:48:fe:6e:
#     5b:79:ab:07:b2:19:58:5e:30:e4:2f:cb:e5:97:23:
#     e5:62:fe:3c:2d:95:6d:e2:b7:6e:64:04:b6:54:a0:
#     44:83:06:0f:87:64:a9:f1:cf:73:20:70:9e:97:ae:
#     83:1d:8c:f3:f0:4c:7d:9f:f2:c3:ab:09:32:35:8c:
#     9c:cd:51:8c:49:f4:94:34:40:f4:eb:c7
# Exponent: 65537 (0x10001)
```

So the flag has been encrypted with AES, and the key was exchanged with RSA.

It's a common use of RSA: since it is computationally intensive only small chunks are encrypted with RSA, like keys.

The name of the challenge points clearly to [this tool][rsa-ctf-tool]:

```shell
rsactftool --publickey sources/pubkey.pem --private
# [*] Testing key sources/pubkey.pem.
# [*] Performing factordb attack on sources/pubkey.pem.
# [*] Performing fibonacci_gcd attack on sources/pubkey.pem.
# 100%|███████████████████████████████████████████████████████████████████████████████████████████| 9999/9999 [00:00<00:00, 19847.46it/s]
# [*] Performing nonRSA attack on sources/pubkey.pem.
# n = 10410080216253956216713537817182443360779235033823514652866757961082890116671874771565125457104853470727423173827404139905383330210096904014560996952285911^3
# d = 129275315911223317359903751663807516352090026808195570114389567583720564611378335627134085402837298827247544997735787221623420069090831026403341043627337118073514316414863510575197151252044137503590414785481554107787977492191190932914467213110568469344259204522660239854742719334572977699979751357274672629248833545002097445009562614595500619383316585368090022534207869125569280525912198666917266810668438225654808711335777444218772562879952971915504193507508773
```

The "nonRSA" attack factors the modulus as a power of a root:

```
10410080216253956216713537817182443360779235033823514652866757961082890116671874771565125457104853470727423173827404139905383330210096904014560996952285911
```

## Decrypting the AES key

The data can be parsed as HEX to perform the math in Python:

```shell
xxd -p -c 1024 sources/flag.txt.aes 
# 4845da3014a52429e914c3117b1c45a0a68d6454e83057af6fcadadae011814d0a
```

```python
CT_FLAG = 0x4845da3014a52429e914c3117b1c45a0a68d6454e83057af6fcadadae011814d0a
CT_KEY = 0x13822f9028b100e2b345a1ad989d9cdedbacc3c706c9454ec7d63abb15b58bef8ba545bb0a3b883f91bf12ca12437eb42e26eff38d0bf4f31cf1ca21c080f11877a7bb5fa8ea97170c932226eab4812c821d082030100030d84ebc63fd8767cde994e0bd1a1f905c27fb0d7adb55e3a1f101d8b5b997ba6b1c09a5e1cc65a9206906ef5e01f13d7beeebdf389610fb54676f76ec0afc51a304403d44bb3c739fd8276f0895c3587a710d15e43fc67284070519e6e0810caf86b134f02ec54018
E = 0x10001
N = 0x77d1e32bfe41fb07612bcb952e8b196d9c303941dd1947d4fb5e0fb80dea75382a1c8c951ce7394408edc801d3cd9bb4c5acd6eb0f61f512aea903b3ed440ebcf3c38d8c1baf3762f2e52517dc3b6b3273e60d2530eab551d6e55dd2349d89f96282c34039f9a6f6a80fac7e144586f3c9ee0b0bbd48fe6e5b79ab07b219585e30e42fcbe59723e562fe3c2d956de2b76e6404b654a04483060f8764a9f1cf7320709e97ae831d8cf3f04c7d9ff2c3ab0932358c9ccd518c49f4943440f4ebc7
P = 0xc6c36983462083ed3b98a4681b44a0a7cbd177d16b41a1ecc924ade2f5e9af0bfc3658e888624f4679240468b4e9a3cc592261e52e9ddee05742ccb1c20aa2d7
```

Since the modulus is a power of a prime number, the [Carmichael function][carmichael-function] evaluates to:

```python
phi = (P - 1) * pow(P, 2) # N = P ** 3 => phi(N) = (P-1) * (P ** 2)
```

Which gives the private exponent and the decrypted key:

```python
d = pow(E, -1, phi)
key = pow(CT_KEY, d, N)
```

## Decrypting the flag

We know the encryption scheme is AES. I found the mode to be `ECB` trough trial and error:

```python
data = pad(bytes.fromhex(hex(CT_FLAG)[2:]),16)
cipher = AES.new(bytes.fromhex(hex(key)[2:]), AES.MODE_ECB)
print(cipher.decrypt(data))
```

> `HTB{pl4y1ng_w1th_pr1m3s_1s_fun!}`

[author-profile]: https://app.hackthebox.com/users/13243
[carmichael-function]: https://en.wikipedia.org/wiki/Carmichael_function
[euler-totient]: https://en.wikipedia.org/wiki/Euler%27s_totient_function
[rsa-ctf-tool]: https://github.com/Ganapati/RsaCtfTool
