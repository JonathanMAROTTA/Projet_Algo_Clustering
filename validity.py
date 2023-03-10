#!/usr/bin/env python3

from itertools import combinations
from collections import defaultdict
from multiprocessing import Pool, cpu_count, Manager, Process
import sys
import os
from time import sleep

from geo.point import Point
from geo.tycat   import tycat

import libtests
import connectes

GRAPH_SIZE = 4
DISTANCE = 1

def main():
    print()

    manager = Manager()

    progress = manager.Value(int, 0)

    progress_process = Process(target=progress_main, args=(progress, 2 ** ( GRAPH_SIZE * GRAPH_SIZE )))
    progress_process.start()

    with Pool(cpu_count() - 1) as pool:
        for nb_points in range(1, GRAPH_SIZE * GRAPH_SIZE + 1):

            for graph in combinations(range(GRAPH_SIZE * GRAPH_SIZE), nb_points):
                pool.apply_async(process_main, (progress, graph))

    progress_process.terminate()

    print("\n  Validation terminée !\n")


def progress_main(current, total):
    while True:
        libtests.printProgressBar(current.value, total)
        sleep(0.5)

def process_main(progress, graph):
    progress.value += 1

    points = [(value % GRAPH_SIZE, value // GRAPH_SIZE) for value in graph]

    groups = defaultdict(set)
    register = {}

    for point_id in range(len(points)):
        register[point_id] = point_id
        groups[point_id].add(point_id)

    for point_id, aside_id in filter(lambda duo: register[duo[0]] != register[duo[1]] and connectes.is_at_distance(points[duo[0]], points[duo[1]], DISTANCE), combinations(range(len(points)), 2)):

        old_ref = register[aside_id]
        groups[register[point_id]].update(groups[old_ref])

        for other_id in groups[old_ref]:
            register[other_id] = register[point_id]

        groups.pop(old_ref)

    counts = list((len(group) for group in groups.values()))
    counts.sort(reverse=True)
        
    sys.stdout = open(os.devnull, 'w')
    
    project_counts = connectes.main_perfs(DISTANCE, points)    
    
    sys.stdout.close()
    sys.stdout = sys.__stdout__

    if counts != project_counts:
        print('\n  --', 'Erreur', '--')
        print('  Attendu : ', counts)
        print('\n  Résultat : ', project_counts)

        tycat(points)


if __name__ == '__main__':
    main()