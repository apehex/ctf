
void FUN_00400978(byte *param_1)

{
  int local_14;
  byte *local_10;
  
  local_14 = 0;
  local_10 = param_1;
  while ((*local_10 != 9 && (local_14 < 0x14))) {
    putchar((int)(char)(*local_10 ^ 9));
    local_10 = local_10 + 1;
    local_14 = local_14 + 1;
  }
  putchar(10);
  return;
}

