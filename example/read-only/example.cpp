#include <iostream>

int main()
{
  std::cout << "Hello, world!";
  return 0;
}

int add_one(int x)
{
  return x + 1;
}

int wrong_arg()
{
  return add_one("3");
}
