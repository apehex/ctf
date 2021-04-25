#include <stdio.h>

char flag[] = "\x41\x5d\x4b\x72\x3d\x39\x6b\x30\x3d\x30\x6f\x30\x3b\x6b\x31\x3f\x6b\x38\x31\x74";

void output() {
  for (int i = 0 ; i < 20 ; i++) {
    putchar((int)(char)(flag[i] ^ 9));
  }
  putchar(10);
  return;
}

int main(int argc, char *argv) {
  output();
}
