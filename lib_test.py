#!/usr/bin/env python3

from time import perf_counter

from geo.tycat   import tycat
from geo.point   import Point
from geo.segment import Segment

# x-------------------x
# |  Tests functions  |
# x-------------------x

# Performances
class Perf():
    """ Classe simplifiant l'observation des perfs grâce à des "with". """

    times = {}

    def __init__(self, index):
        """ Permet de choisir sous quel index sotcker la performance. """

        if index not in Perf.times:
            Perf.times[index] = 0

        self.index = index
        self.start = 0

    def __enter__(self):
        """ Call with "with". """
        self.start = perf_counter()

        return self

    def __exit__(self, type, value, traceback):
        """ Call after "with" block. """

        Perf.times[self.index] += perf_counter() - self.start


# Compte-rendu
def test_rapport(points, buckets, BUCKET_SIZE, groups):
    # Graphs

    # Tests
    segments = { 'finals': { 'groups': [], 'fusions': [], 'buckets': [] } }

    for i, group in groups.items():
        for j in group:
            segments['finals']['groups'].append((points[i], points[j]))

    for b in buckets.keys():
        segments['finals']['buckets'].append(((0, int(b) * BUCKET_SIZE), (1, int(b) * BUCKET_SIZE)))

    if len(points) <= 1000:
        for graph in segments.values():
            graph_segment = []

            for linked_segment in graph.values():
                graph_segment.append([Segment([Point(list(p1)), Point(list(p2))]) for p1, p2 in linked_segment])

            tycat([Point(point) for point in points], *graph_segment)

        print('')

    # -- Performances --
    percent = 100 / Perf.times[0]

    print('  Performances :')

    print("  x----------x----------------x----------x")
    print("  | Total    | Sections       | Percents |")
    print("  x----------x----------------x----------x")
    print(f"  | {Perf.times[0]:8.5f} | Initialization |   {(Perf.times[1] * percent):5.2f}% |")
    print("  |          x----------------x----------x")
    print(f"  |          | Init           |   {(Perf.times[2] * percent):5.2f}% |")
    print(f"  |          | Groups         |   {(Perf.times[3] * percent):5.2f}% |")
    print(f"  |          | Fusions        |   {(Perf.times[6] * percent):5.2f}% |")
    print("  x----------x----------------x----------x")
    print("  Nombre de points :",len(points), '\n')
