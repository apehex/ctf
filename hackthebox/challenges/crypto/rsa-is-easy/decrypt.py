#!/usr/bin/env python3
from Crypto.Util.number import bytes_to_long, getPrime, isPrime, inverse
from os import urandom

def extended_euclid_gcd(a, b):
    """
    Returns a list `result` of size 3 where:
    Referring to the equation ax + by = gcd(a, b)
        result[0] is gcd(a, b)
        result[1] is x
        result[2] is y
    """
    s = 0; old_s = 1
    t = 1; old_t = 0
    r = b; old_r = a

    while r != 0:
        quotient = old_r//r
        old_r, r = r, old_r - quotient*r
        old_s, s = s, old_s - quotient*s
        old_t, t = t, old_t - quotient*t
    return [old_r, old_s, old_t]

e = 0x10001
n1 = 101302608234750530215072272904674037076286246679691423280860345380727387460347553585319149306846617895151397345134725469568034944362725840889803514170441153452816738520513986621545456486260186057658467757935510362350710672577390455772286945685838373154626020209228183673388592030449624410459900543470481715269
c1 = 92506893588979548794790672542461288412902813248116064711808481112865246689691740816363092933206841082369015763989265012104504500670878633324061404374817814507356553697459987468562146726510492528932139036063681327547916073034377647100888763559498314765496171327071015998871821569774481702484239056959316014064
c2 = 46096854429474193473315622000700040188659289972305530955007054362815555622172000229584906225161285873027049199121215251038480738839915061587734141659589689176363962259066462128434796823277974789556411556028716349578708536050061871052948425521408788256153194537438422533790942307426802114531079426322801866673

# if n1 > n2 (p > z) then (n1 * E + n2) % n1 = n2
F = 601613204734044874510382122719388369424704454445440856955212747733856646787417730534645761871794607755794569926160226856377491672497901427125762773794612714954548970049734347216746397532291215057264241745928752782099454036635249993278807842576939476615587990343335792606509594080976599605315657632227121700808996847129758656266941422227113386647519604149159248887809688029519252391934671647670787874483702292498358573950359909165677642135389614863992438265717898239252246163
E = F // n1
n2 = F % n1

q, x, y = extended_euclid_gcd(n1, n2)
p = n1 // q
z = n2 // q

lambda1 = ((p -1 ) * (q - 1)) // extended_euclid_gcd(p - 1, q - 1)[0]
lambda2 = ((q -1 ) * (z - 1)) // extended_euclid_gcd(q - 1, z - 1)[0]

d1 = inverse(e, lambda1)
d2 = inverse(e, lambda2)

f1 = pow(c1, d1, n1)
f2 = pow(c2, d2, n2)

print(bytes.fromhex(hex(f1)[2:]))
print(bytes.fromhex(hex(f2)[2:]))