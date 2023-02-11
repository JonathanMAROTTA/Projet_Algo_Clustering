#!/usr/bin/env python3

from random import uniform

print('0.15')

for _ in range(1000000):
    print(f"{uniform(0,1):7f}, {uniform(0,1):7f}")
