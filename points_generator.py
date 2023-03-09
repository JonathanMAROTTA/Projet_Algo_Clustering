#!/usr/bin/env python3

from random import uniform
import sys

print(sys.argv[1])

for _ in range(int(sys.argv[2])):
    print(f"{uniform(0,1)}, {uniform(0,1)}")
