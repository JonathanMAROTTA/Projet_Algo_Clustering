#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from math import cos, sin, pi, floor
from sys import argv
from itertools import islice, cycle, product
from collections import defaultdict
from time import perf_counter
import random
from multiprocessing import Process, Manager

from graph_multiprocessing import graph_multiprocessing

from geo.tycat import tycat
from geo.point import Point
from geo.segment import Segment

# x------------------x
# |  File Managment  |
# x------------------x

def load_instance(filename):
    """
    loads .pts file.
    returns distance limit and points.
    """
    with open(filename, "r", encoding="utf-8") as instance_file:
        lines = iter(instance_file)
        distance = float(next(lines))
        points = [tuple(float(f) for f in l.split(",")) for l in lines]

    return distance, points


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

# Tables
def _separation(*sizes):
    """ Affiche une ligne horizontale pour les tables. """

    print('  ', end='')

    for config in sizes:
        for _ in range(config[1]):
            print('-' * config[0], 'x', sep='', end='')
    print('')
def _head(size, *others):
    """ Affiche l'en-tête pour les tables. """

    print('     |', end='')

    for i in range(size):
        print(f" {i:2} |", end="")

    for name in others:
        print(f" {name} |", end='')
    print('')

def set_color(text, color):
    """ Retourne le code couleur demandé. """

    code = '0'

    if color == 'black':
        code = "30"
    elif color == 'red':
        code = "31"
    elif color == 'green':
        code = "32"
    elif color == 'yellow':
        code = "33"
    elif color == 'blue':
        code = "34"
    elif color == 'magenta':
        code = "35"
    elif color == 'cyan':
        code = "36"
    elif color == 'white':
        code = "37"
    elif color == 'gray':
        code = "90"

    return f"\x1b[{code}m{text}\x1b[0m"
def table(x_length, y_length):
    """ Créer un générateur permettant la génération de tables. """

    _head(x_length)
    _separation((3, 1), (4, x_length))

    for y in range(y_length):
        print(f"  {y:2} | ", end='')

        for x in range(x_length):
            yield x, y

            print(" | ", end='')

        print('')

        _separation((3, 1), (4, x_length))


# x----------x
# |  Points  |
# x----------x

def is_at_distance(point_1, point_2, distance):
    """
        Def: Retourne le booléen indiquant si la distance en dimension 2
             entre les deux points est inférieure ou égale à la distance donnée.
        Pre-conditions:
        - point_1 et point_2 sont des coordonnées de points
        - distance est un réel positif.
        Post-conditions : ...
    """

    dx, dy = point_2[0] - point_1[0], point_2[1] - point_1[1]
    return dx*dx + dy*dy <= distance * distance


# x-----------x
# |  Buckets  |
# x-----------x

def analyse_bucket(bucket_id, plan_shortcut, clustering_shortcut):
    buckets_begins = defaultdict(lambda: 0)

    # Shortcut development
    points, buckets, distance = plan_shortcut
    register, groups, fusions = clustering_shortcut

    bucket_point_id = 0
    bucket = buckets[bucket_id]

    while bucket_point_id < len(buckets[bucket_id]) and buckets[bucket_id][bucket_point_id] in register.keys():
        bucket_point_id += 1

    while bucket_point_id < len(bucket):

        # x------------------x
        # |  Initialization  |
        # x------------------x

        # Components
        point_id = bucket[bucket_point_id]
        point = points[point_id]

        groups[point_id] = set([point_id])
        register[point_id] = point_id

        next_index = len(bucket)

        # x----------x
        # |  Groups  |
        # x----------x

        # Previous
        for _, aside_id in iter_bucket(points, distance, buckets, buckets_begins, point_id, bucket_id - 1):

            if is_at_distance(point, points[aside_id], distance):

                if aside_id in register:

                    fusions[point_id].add(register[aside_id])

                else:

                    groups[point_id].add(aside_id)
                    register[aside_id] = point_id

        # Current
        for bucket_point_id, aside_id in iter_bucket(points, distance, buckets, buckets_begins, point_id, bucket_id):

            if aside_id != point_id:

                if aside_id in register:

                    if is_at_distance(point, points[aside_id], distance):
                        fusions[point_id].add(register[aside_id])

                else:
                    if is_at_distance(point, points[aside_id], distance):
                        groups[point_id].add(aside_id)
                        register[aside_id] = point_id
                        
                    else:
                        next_index = min(next_index, bucket_point_id)

        # Next index
        while bucket_point_id < len(bucket) and bucket[bucket_point_id] in register.keys():
            bucket_point_id += 1

        # x-----------x
        # |  Fusions  |
        # x-----------x

        # Suppression partielle des set de fusions de taille 1
        if point_id in fusions and len(fusions[point_id]) == 1:
            aside_id = fusions[point_id].pop()

            fusions[aside_id].add(point_id)
            fusions.pop(point_id)



        # Next 
        bucket_point_id = min(next_index, bucket_point_id)



def iter_bucket(points, distance, buckets, buckets_begins, current_index, bucket_id):
    point = points[current_index]

    # Observation des buckets à une distance de plus ou moins 4 du bucket courant
    bucket = buckets[bucket_id]

    i = buckets_begins[bucket_id]

    # Removing
    while i < len(bucket) and points[bucket[i]][0] <  point[0] - distance:
        i += 1

    buckets_begins[bucket_id] = i

    # Efficient
    while i < len(bucket) and points[bucket[i]][0] <= point[0] + distance:

        yield i, bucket[i]
        i += 1

# x--------x
# |  Main  |
# x--------x

def print_components_sizes(distance, points):
    """
    affichage des tailles triees de chaque composante
    """

    with Perf(0):

        # x------------------x
        # |  Initialization  |
        # x------------------x

        with Perf(1):
            points.sort()

            # Constantes
            BUCKET_SIZE = distance

            # Buckets
            buckets = defaultdict(list)
            plan_shortcut = (points, buckets, distance)

            for i, point in enumerate(points):
                buckets[int(point[1] // BUCKET_SIZE)].append(i)

            buckets_keys = list(buckets.keys())
            buckets_keys.sort()

            # Clustering
            clustering_shortcut = ({}, {}, defaultdict(set))
            register, groups, fusions = clustering_shortcut
            

        # x-------------x
        # |  Processes  |
        # x-------------x

        with Perf(3):
            graph_multiprocessing(buckets_keys, analyse_bucket, plan_shortcut, clustering_shortcut)

        print('\n  Multiprocessing done...')
        # print('Affichage des fusions:')
        # for i, group in fusions.items():
        #     print(f"  - {i:3} ({points[i][1] // BUCKET_SIZE:2.0f}) : ", end='')
        #     for j in group:
        #         print(f"{j:3}, ", end='')
        #     print('')


        # Isolates link
        with Perf(4):
            buckets_begins = defaultdict(int)

            buckets_keys.sort()
            
            for bucket_id in buckets_keys:

                buckets_begins.clear()

                for i in buckets[bucket_id]:

                    if i not in fusions.keys():

                        point = points[i]

                        for relative_bucket_id in range(max(bucket_id - 1, 0), bucket_id + 1):
                            for _, aside_id in iter_bucket(points, distance, buckets, buckets_begins, i, relative_bucket_id):

                                if register[aside_id] != register[i] and register[i] not in fusions[register[aside_id]] and register[aside_id] not in fusions[register[i]]:
                                    
                                    if is_at_distance(point, points[aside_id], distance):

                                        fusions[register[i]].add(register[aside_id])

        # x-----------x
        # |  Fusions  |
        # x-----------x

        with Perf(7):
            for i, near_groups in fusions.items():

                # Mise à jour du registre
                for group_id in near_groups:
                    register_id = register[group_id]

                    if register_id != register[i]:
                        groups[register[i]].update(groups[register_id])

                        for point_id in groups[register_id]:
                            register[point_id] = register[i]

                        groups.pop(register_id)


        # Calcul du résultat
        counts = list((len(group) for group in groups.values()))
        counts.sort(reverse=True)

        print('\n  ', counts, sep='', end='\n')


        segments = { 'finals': { 'groups': [] } }
        for i, group in groups.items():
            for j in group:
                segments['finals']['groups'].append((points[i], points[j]))



    # x---------x
    # |  Tests  |
    # x---------x

    # Graphs
    if len(points) <= 1000:
        for graph in segments.values():
            graph_segment = []

            for linked_segment in graph.values():
                graph_segment.append([Segment([Point(list(p1)), Point(list(p2))]) for p1, p2 in linked_segment])

            tycat([Point(point) for point in points], *graph_segment)

        print('')

    # Comparaisons
    # if len(points) <= 45:
    #     for j, i in table(len(points), len(points)):

    #         if i == j:
    #             print(set_color('--', 'red'), end='')

    #         elif tests[i][j] > 0:
    #             color = 'magenta' if tests[j][i] > 0 else \
    #                     'yellow'  if tests[i][j] > 1 else 'white'

    #             print(set_color(f"{tests[i][j]:2}", color), end='')
    #         else:
    #             print("  ", end='')

    # total = 0
    # for line in tests.values():
    #     for count in line.values():
    #         total += count

    # print(f"  Total des comparaisons : {total} ({total * 100 / (len(points) * len(points)):.5f}%)", '\n')


    # -- Performances --
    percent = 100 / Perf.times[0]

    print('  Performances :')

    print("  x----------x----------------x----------x")
    print("  | Total    | Sections       | Percents |")
    print("  x----------x----------------x----------x")
    print(f"  | {Perf.times[0]:8.5f} | Initialization |   {(Perf.times[1] * percent):5.2f}% |")
    print("  |          x----------------x----------x")
    # print(f"  |          | Initialization |   {(Perf.times[2] * percent):5.2f}% |")
    print(f"  |          | Groups         |   {(Perf.times[3] * percent):5.2f}% |")
    print(f"  |          | Isolates       |   {(Perf.times[4] * percent):5.2f}% |")
    # print(f"  |          | Links          |   {(Perf.times[6] * percent):5.2f}% |")
    print(f"  |          | Fusions        |   {(Perf.times[7] * percent):5.2f}% |")
    print("  x----------x----------------x----------x")
    print("  Nombre de points :",len(points), '\n')

    print('  ', counts, '\n', sep='')


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
