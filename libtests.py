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

    def __init__(self, title, is_main = False):
        """ Permet de choisir sous quel index sotcker la performance. """

        if title not in Perf.times:
            Perf.times[title] = [0, is_main]

        self.title = title

    def __enter__(self):
        """ Call with "with". """
        self.start = perf_counter()

        return self

    def __exit__(self, type, value, traceback):
        """ Call after "with" block. """

        Perf.times[self.title][0] += perf_counter() - self.start

    @staticmethod
    def reset():
        Perf.times.clear()

    @staticmethod
    def display():
        main_title = None
        for title in filter(lambda title: Perf.times[title][1], Perf.times):
            main_title = title
            break

        percent = 100 / Perf.times[main_title][0]

        print('\n  Performances :')
        print("  x-----------------x----------x----------x")
        print("  | Sections        | Time     | Percents |")
        print("  x-----------------x----------x----------x")

        print(f"  | {main_title:15} | {Perf.times[main_title][0]:7.4f}s |          |")
        print("  x-----------------x----------x----------x")

        for title, time in filter(lambda record: not record[1][1], Perf.times.items()):
            print(f"  | {title:15} | {time[0]:7.4f}s | {(time[0] * percent):7.3f}% |")

        print("  x-----------------x----------x----------x")


# Compte-rendu
def test_rapport(points, buckets, BUCKET_SIZE, groups, segments):

    # -- Graphs --

    # Buckets
    segments['buckets'] = []

    for b in buckets.keys():
        segments['buckets'].append(((0, int(b) * BUCKET_SIZE), (1, int(b) * BUCKET_SIZE)))

    # Display
    if len(points) <= 1000:
        graph_segment = []

        for linked_segment in segments.values():
            graph_segment.append([Segment([Point(list(p1)), Point(list(p2))]) for p1, p2 in linked_segment])

        # tycat([Point(point) for point in points], *graph_segment)

        print('')

    # -- Performances --

    Perf.display()
    print("  Nombre de points :",len(points), '\n')


# Ficher de tests
def printProgressBar(iteration, total):
    percent = ("{0:.2f}").format(100 * (iteration / float(total)))
    filledLength = int(50 * iteration // total)
    bar = '█' * filledLength + '-' * (50 - filledLength)

    print(f'\r  Progression : |{bar}| {percent}%', end = '\r')

    if iteration == total: 
        print()