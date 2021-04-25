void output(char *input) {
  int i;
  char *c;

  i = 0;
  c = input;
  while ((*c != 9 && (i < 20))) {
    putchar((int)(char)(*c ^ 9));
    c = c + 1;
    i = i + 1;
  }
  putchar(10);
  return;
}
