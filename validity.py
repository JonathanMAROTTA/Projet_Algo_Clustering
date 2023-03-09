#!/usr/bin/env python3

from itertools import combinations
from collections import defaultdict
import sys
import os

from geo.point import Point
from geo.tycat   import tycat

import libtests
import connectes

GRAPH_SIZE = 4
DISTANCE = 1.5

def main():
    print()

    for nb_points in range(1, GRAPH_SIZE * GRAPH_SIZE + 1):

        libtests.printProgressBar(nb_points, GRAPH_SIZE * GRAPH_SIZE)

        for graph in combinations(range(GRAPH_SIZE * GRAPH_SIZE), nb_points):

            points = []
            groups = defaultdict(set)
            register = {}

            with open('.validity/points.txt', 'w+') as file:
                file.write(f"{DISTANCE}\n")

                for value in graph:
                    x, y = value % GRAPH_SIZE, value // GRAPH_SIZE
                    file.write(f"{x}, {y}\n")

                    points.append(Point((x, y)))

            for point_id in range(len(points)):
                register[point_id] = point_id
                groups[point_id].add(point_id)

            for point_id, aside_id in filter(lambda duo: register[duo[0]] != register[duo[1]] and points[duo[0]].distance_to(points[duo[1]]) <= DISTANCE, combinations(range(len(points)), 2)):

                old_ref = register[aside_id]
                groups[register[point_id]].update(groups[old_ref])

                for other_id in groups[old_ref]:
                    register[other_id] = register[point_id]

                groups.pop(old_ref)

            counts = list((len(group) for group in groups.values()))
            counts.sort(reverse=True)
                
            sys.stdout = open(os.devnull, 'w')
            project_counts = connectes.main_perfs([".validity/points.txt"])    
            sys.stdout = sys.__stdout__

            if counts != project_counts:
                print('\n  --', 'Erreur', '--')
                print('  Attendu : ', counts)
                print('\n  Résultat : ', project_counts)

                tycat(points)

                return

    print()


if __name__ == '__main__':
    main()