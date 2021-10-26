#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  if (argc != 2) {
    printf("usage: %s filename", argv[0]);
    return 1;
  }
  char cwd[100];
  if (getcwd(cwd, sizeof(cwd)) != NULL) {
    printf("Current working dir: %s\n", cwd);
  } else {
    perror("getcwd() error");
    return 1;
  }
  FILE *fp = fopen(argv[1], "r");
  
  int maximumLineLength = 128;
  char *lineBuffer = (char *)malloc(sizeof(char) * maximumLineLength);

  char ch = getc(fp);
  int count = 0;
  while ((ch != '\n') && (ch != EOF)) {
    lineBuffer[count] = ch;
    count++;
    ch = getc(fp);
  }
  fclose(fp);
  printf("%s", lineBuffer);
  return 0;
}