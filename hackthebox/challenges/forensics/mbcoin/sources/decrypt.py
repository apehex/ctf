PAYLOADS = [
	{
		'inpath': '../payloads/dll/pt.html',
		'outpath': '../payloads/dll/www1.dll',
		'key': b'6iIgloMk5iRYAw7ZTWed0CrjuZ9wijyQDjKO9Ms0D8K0Z2H5MX6wyOKqFxlOm1XpjmYfaQXacA6'},
	{
		'inpath': '../payloads/dll/vm.html',
		'outpath': '../payloads/dll/www4.dll',
		'key': b'6iIoNoMk5iRYAw7ZTWed0CrjuZ9wijyQDjPy9Ms0D8K0Z2H5MX6wyOKqFxlOm1GpjmYfaQXacA6'}]

#================================================================== xor utility

def xor(data: bytes, key: bytes) -> bytes:
	return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

#=========================================================== decrypting the dll

for __payload in PAYLOADS:
	with open(__payload['inpath'], 'rb') as __infile:
		__raw = __infile.read()
		__clear = xor(__raw, __payload['key'])
		with open(__payload['outpath'], 'wb') as __outfile:
			__outfile.write(__clear)
