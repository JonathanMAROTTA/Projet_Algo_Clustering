#!/usr/bin/env python3

import os
import sys
from sys import argv
from itertools import product
from random import uniform
from collections import defaultdict
from time import perf_counter, time
import connectes
from multiprocessing import Pool, cpu_count, Manager

import matplotlib.pyplot as plt

DISTANCE_NEGATIVE_10_POW_MIN = 1
DISTANCE_NEGATIVE_10_POW_MAX = 5

NB_POINTS = 100
STEP = 1

CALL_COUNT = 10


def main():
    print()

    manager = Manager()

    results = []
    sums = manager.dict()
    averages = defaultdict(float)

    for negative_pow in range(DISTANCE_NEGATIVE_10_POW_MIN, DISTANCE_NEGATIVE_10_POW_MAX + 1):
    
        sums.clear()
        distance = 10**(-negative_pow)

        # Create files
        for test_number in range(0, CALL_COUNT):
            with open(f"{os.path.dirname(__file__)}/.perfs/points-{test_number}.txt", "w+") as file:
                file.write(f'{distance}\n')

        for step_id in range(1, ( NB_POINTS // STEP ) + 1):
       
            nb_points = step_id * STEP
            sums[nb_points] = 0.0

            printProgressBar(step_id, NB_POINTS // STEP)

            for test_number in range(0, CALL_COUNT):
                with open(f"{os.path.dirname(__file__)}/.perfs/points-{test_number}.txt", "a") as file:
                    file.write(f"{uniform(0,1)}, {uniform(0,1)}\n" * STEP)

            pool = Pool(cpu_count())

            for test_number in range(0, CALL_COUNT):
                # process_main(sums, test_number, nb_points)
                pool.apply_async(process_main, (sums, test_number, nb_points))
                    
            pool.close()
            pool.join()
                
            averages[nb_points] = sums[nb_points] / float(CALL_COUNT)

        results.append(averages.copy())

    for i, result in enumerate(results):
        plt.plot([effectif for effectif in result.keys()], [time for time in result.values()], ['r','b','g','m','y'][i])
   
    plt.ylabel('AVG Times')
    plt.xlabel('Effectif')
    plt.show()


def printProgressBar(iteration, total):
    percent = ("{0:.2f}").format(100 * (iteration / float(total)))
    filledLength = int(50 * iteration // total)
    bar = '█' * filledLength + '-' * (50 - filledLength)

    print(f'\r  Progression : |{bar}| {percent}%', end = '\r')

    if iteration == total: 
        print()


def process_main(sums, test_number, nb_points):
    sys.stdout = open(os.devnull, 'w')

    start = perf_counter()
    connectes.main_perfs([f".perfs/points-{test_number}.txt"])
    sums[nb_points] += perf_counter() - start

    sys.stdout = sys.__stdout__

if __name__ == '__main__':
    main()