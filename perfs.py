#!/usr/bin/env python3

import os
import sys
from itertools import product
from random import uniform
from collections import defaultdict
import connectes
import libtests
import matplotlib.pyplot as plt
from libtests import Perf
from geo.point import Point
import libtests

DISTANCES = [ 0.1, 0.075, 0.05, 0.025 ]

NB_POINTS = 10000
STEP = 1000

CALL_PRECISION = 10


def main():
    print()
    plt.ylabel('AVG Times')
    plt.xlabel('Effectif')

    # Progress
    total_try, current_try = len(DISTANCES) * (NB_POINTS // STEP) * CALL_PRECISION, 0

    # Build sums
    sums, averages = defaultdict(list), defaultdict(list)
    for dist_key, _ in product(range(len(DISTANCES)), range(NB_POINTS // STEP)):
        sums[dist_key].append(0.0)

    with open(os.devnull, 'w') as out_null:
        for prog_call in range (1, CALL_PRECISION + 1):
            points_lists = []

            # For each steps
            for step_id in range(NB_POINTS // STEP):

                # Add points
                points_lists.extend((uniform(0,1), uniform(0,1)) for _ in range(STEP))

                # For each negative pow
                for dist_key, distance in enumerate(DISTANCES):
                    current_try += 1
                    libtests.printProgressBar(current_try, total_try)

                    # -- Run average --
                    sys.stdout = out_null

                    Perf.reset()
                
                    with Perf("perf"):
                        connectes.main_perfs(distance, points_lists)
                    
                    sums[dist_key][step_id] += Perf.times["perf"][0]
                    sys.stdout = sys.__stdout__

            averages.clear()
            for dist_key, step_id in product(range(len(DISTANCES)), range(NB_POINTS // STEP)):
                averages[dist_key].append(sums[dist_key][step_id] / float(prog_call))

            plt.clf()

            for dist_key, result in averages.items():
                plt.plot([(step + 1) * STEP for step in range(len(result))], result, ['r','b','g','m','y'][dist_key])

            plt.legend(DISTANCES)

            # plt.show()
            plt.pause(0.1)

    print("\n  Au revoir !\n")

    plt.show()

if __name__ == '__main__':
    main()