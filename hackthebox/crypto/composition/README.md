> The more the merrier, right? We decided to mash two of the best cryptosytems
> together for the best product. Our new encryption scheme is up and running and
> this time it is unbreakable! To prove that, we have also released its source
> code and a test center where you can test it out!

> Author: **[DaysOfLife][author-profile]**

## Browsing

```
Welcome to the ECRSA test center. Your encrypted data will be sent soon.
Please check the logs for the parameters.
Generating your key...
Creating ECC params
Encrypted flag: 11527ef661b63f0e8df26e78d79b614cb63e834da05bf333856a97f81d74aec58aefbda52dd6ee164447cb3cd64869aee935d9e961ea12375354eea7e21a6790
IV: 2d2e1e8a88205995ce2d76d244c28b2b
N: 6977872954453287113318928946533004640573076971270404736649857554109814714767232598626781851567154954553736188657231769647898054950996488674893670519816653
ECRSA Ciphertext: Point(x=2851572783042418026133996814250879893796058672204604585672807372129430580698309059946087548171123066371647509247443388126483506717427455136382648462997156, y=6229895414423825093970708176923792736711251122090113458666591518448699655186597924150954711460449644605774495375106765029330485916590545376676075133841422)
Would you like to test the ECRSA curve?
[y/n]> y
Generating random point...
Point(x=4462129553869194635110347913537781447163673151204817501735057255299985150330059138351040776905457304373656070189763506501461514517702259280043082926076418, y=1012904040892509457148773549664059101097406279754569553936756270049573187157782900888372009243941138782308618768537282105721569482060963331594736944741842)
Thanks for testing!
```

```python
cipher = AES.new(key,AES.MODE_CBC,iv)
data = cipher.encrypt(pad(flag,16))
print(f"Encrypted flag: {data.hex()}")
```

```python
key = md5(str(g.x).encode()).digest()
iv = os.urandom(16)
print(f"IV: {iv.hex()}")
```

```python
ec = EllipticCurve(a,b,n)
g = getrandpoint(ec,p,q)
A = ec.multiply(g,e)
print(f"ECRSA Ciphertext: {A}")
```

The random point has a quadratic residue as abscissa.

```python
def getrandpoint(ec,p,q):
    num = random.randint(1,p*q)
    while legendre(expr(num),p) != 1 or legendre(expr(num),q) != 1:
        num = random.randint(1,p*q)
    return ec.lift_x(num,p,q)
print("Generating random point...")
print(getrandpoint(ec,p,q))
```

- discriminant != 0
- 

## Factoring N

```python
def keygen(bits):
    # Returns RSA key in form ((e,n),(p,q))
    p = getPrime(bits // 2)
    while p % 4 == 1:
        p = next_prime(p)
    e = next_prime(p >> (bits // 4))
    q = next_prime(p)
    for i in range(50):
        q = next_prime(q)
    while q % 4 == 1:
        q = next_prime(q)
    n = p * q
    if n.bit_length() != bits:
        return keygen(bits)
    return (e,n),(p,q)
```

[author-profile]: https://app.hackthebox.eu/users/185587
