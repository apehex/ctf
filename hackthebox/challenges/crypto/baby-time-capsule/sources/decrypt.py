import math

#################################################################### parameters

CT1 = int('6CEF670EFD22F3B8E6D572602260981937CEB54A77DFBDDBA3E2EE0A6315609EE90BCA9F9C9AD03A940F43334E874625FC6C4221957EE8F99DE19832EEE491159604C11329C92D6AB54455A79703DE036B337231D0BA205F8A2B17F630DF65A74E9D2B72AC2EE70A93CE1DA0C7CAD8026391FC3F09BBA30A135AB6677B50A662', 16)
CT2 = int('4419A97E9AFA596AB476FC9CE53CC171502EF560146DEC41C29E6B906D3A8AFE27D861DD47D5B06718D34C2AD0C5CCB634E0882586D225F7E4CE694497D184E03521B5C3AC5C2A41291751062E8704B43E4AB496B7D1439449770F777A62846EE8C25750B242E7C13C4A75166E264A33C786F037472D2D7FCECE6E158DD85E64', 16)

N1 = int('8A02BAB4D008951AC4D0C6A5459E3A699896E3B9945490BF805C69564F8D8337D530A3EB952B42D283A4C4D7D2E76B5ADDA66D473F12DA5CDF575CF6CD8C11BB1D1EA3C57910B230AA51BD2CB36372E0CA224B3C1718C47C815388925835910B1508CE2AD2B1238BD1C5FD05AE01A89033F43F1ACC78106BD179119377F99D41', 16)
N2 = int('D65C8DDCC51DAA3F181CD7130FCD20C0018F0D0ED123AEC632D88793A905EA84C957B2977B5B5E66FAB19A29FB0D31AAFEC411F86DFB62B7F7FEAAB7838C4A9E2B6418EFEC3871540B08CDF409E3892BBD10F61A25759538F13B629DC6CBA03AE6C3EFDE2C8B0C72218707F9F6666970A0D0D10EAF52133C955A6C50CC072F97', 16)
E = 5

########################################################################### CRT

def crt(congruences, moduli):
    assert len(congruences) == len(moduli)

    _k = len(moduli)
    _product = math.prod(moduli)
    _basis = [_product // moduli[i] for i in range(_k)]
    _inverses = [pow(_basis[i], -1, moduli[i]) for i in range(_k)]

    r = sum([congruences[i] * _basis[i] * _inverses[i] for i in range(_k)])
    return r % _product

######################################################## root

def nth_root(x, n):
    # Start with some reasonable bounds around the nth root.
    upper_bound = 1
    while upper_bound ** n <= x:
        upper_bound *= 2
    lower_bound = upper_bound // 2
    # Keep searching for a better result as long as the bounds make sense.
    while lower_bound < upper_bound:
        mid = (lower_bound + upper_bound) // 2
        mid_nth = mid ** n
        if lower_bound < mid and mid_nth < x:
            lower_bound = mid
        elif upper_bound > mid and mid_nth > x:
            upper_bound = mid
        else:
            # Found perfect nth root.
            return mid
    return mid + 1

######################################################### process

m_5 = crt([CT1, CT2], [N1, N2])
root = nth_root(m_5, 5)

########################################################## display

print(bytes.fromhex(hex(root)[2:]))
