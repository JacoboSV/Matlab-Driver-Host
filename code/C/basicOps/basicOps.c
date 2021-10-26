#include <stdio.h>
#include <stdlib.h>
#include <string.h>

float max(float x, float y) {
  return (x > y) ? x : y;
}

int main(int argc, char *argv[]) {
  if (argc != 4) {
    printf("usage: %s maximum x y", argv[0]);
    return 1;
  }
  char *operation = argv[1];
  float operand1 = atof(argv[2]),
        operand2 = atof(argv[3]);

  if (strcmp("maximum", operation)) {
    printf("Unknown operation: %s", operation);
    return 1;
  }  
  float result = max(operand1, operand2);
  printf("%f", result);
  return 0;
}