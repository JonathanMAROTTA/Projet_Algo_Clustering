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
DISTANCE = 0.5

def main():
    print()

    # Progress
    total_try, current_try = 2 ** ( GRAPH_SIZE * GRAPH_SIZE ), 0

    # N2 Algo
    groups, register = defaultdict(set), {}

    with open(os.devnull, 'w') as out_null:
        for nb_points in range(1, GRAPH_SIZE * GRAPH_SIZE + 1):
            for graph in combinations(range(GRAPH_SIZE * GRAPH_SIZE), nb_points):
                current_try += 1
                libtests.printProgressBar(current_try, total_try)
                
                # -- Run n2 algo --
                points = [(value % GRAPH_SIZE - (GRAPH_SIZE // 2), value // GRAPH_SIZE - (GRAPH_SIZE // 2)) for value in graph]

                groups.clear()
                register.clear()

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
                    
                # -- Run better algo --
                sys.stdout = out_null
                project_counts = connectes.main_perfs(DISTANCE, points)    
                sys.stdout = sys.__stdout__

                # Différent result
                if counts != project_counts:
                    print('\n  --', 'Erreur', '--')
                    print('  Points :', points)
                    print('  Attendu : ', counts)
                    print('\n  Résultat : ', project_counts)

                    with open('test-fail.txt', 'w') as file:
                        file.write(f"{DISTANCE}\n")

                        for point in points:
                            file.write(f"{point[0]}, {point[1]}\n")

                    tycat([Point(point) for point in points])

                    return

    libtests.printProgressBar(1, 1)

    print("\n  Validation terminée !\n")



if __name__ == '__main__':
    main()