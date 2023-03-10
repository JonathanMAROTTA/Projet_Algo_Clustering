#!/usr/bin/env python3

import os
import sys
from sys import argv
from itertools import product
from random import uniform
from collections import defaultdict
from time import perf_counter, time, sleep
import connectes
from multiprocessing import Pool, cpu_count, Manager, Process
import libtests
import matplotlib.pyplot as plt
from libtests import Perf
from geo.point import Point

DISTANCES = [ 0.1, 0.05, 0.01 ]

NB_POINTS = 10000
STEP = 1000

CALL_PRECISION = 10


def main():
    print()
    plt.ylabel('AVG Times')
    plt.xlabel('Effectif')

    manager = Manager()

    # Build sums
    sums = manager.dict()
    for dist_key in range(len(DISTANCES)):
        sums[dist_key] = manager.list()

        for step_id in range(NB_POINTS // STEP):
            sums[dist_key].append(0.0)

    progress = manager.Value(int, 0)

    progress_process = Process(target=progress_main, args=(progress, len(DISTANCES) * (NB_POINTS // STEP) * CALL_PRECISION))
    progress_process.start()

    for prog_call in range (1, CALL_PRECISION + 1):
        points_lists = []

        # For each steps
        pool = Pool(cpu_count() - 1)

        for step_id in range(NB_POINTS // STEP):

            # Add points
            points_lists.extend((uniform(0,1), uniform(0,1)) for _ in range(STEP))
            points_copy = points_lists.copy()

            # For each negative pow
            for dist_key, distance in enumerate(DISTANCES):
                pool.apply_async(process_main, (progress, sums, dist_key, step_id, distance, points_copy))

        pool.close()
        pool.join()

        averages = defaultdict(list)
        for dist_key in range(len(DISTANCES)):
            for step_id in range(NB_POINTS // STEP):
                averages[dist_key].append(sums[dist_key][step_id] / float(prog_call))

        plt.clf()

        for dist_key, result in averages.items():
            plt.plot([(step + 1) * STEP for step in range(len(result))], result, ['r','b','g','m','y'][dist_key])

        plt.legend(DISTANCES)

        # plt.show()
        plt.pause(0.05)

    progress_process.terminate()
    print("\n  Au revoir !\n")

    plt.show()


def progress_main(current, total):
    while True:
        libtests.printProgressBar(current.value, total)
        sleep(0.5)

def process_main(progress, sums, dist_key, step_id, distance, points):
    sys.stdout = open(os.devnull, 'w')

    Perf.reset()
 
    progress.value += 1

    connectes.main_perfs(distance, points)
    sums[dist_key][step_id] += Perf.times["Global"][0]

    sys.stdout.close()
    sys.stdout = sys.__stdout__

if __name__ == '__main__':
    main()