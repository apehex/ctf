CT = bytes.fromhex("6e0a9372ec49a3f6930ed8723f9df6f6720ed8d89dc4937222ec7214d89d1e0e352ce0aa6ec82bf622227bb70e7fb7352249b7d893c493d8539dec8fb7935d490e7f9d22ec89b7a322ec8fd80e7f8921")

def decrypt(b: int) -> int:
  return ((b - 18) * 179) % 256

print(bytes([decrypt(b) for b in CT]))
