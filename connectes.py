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

def iter_bucket(points, bucket, current_index, x_limit, strict = False):
    """
        Def: Permet d'itérer sur un bucket jusqu'à la condition limite en x.
        Pre-conditions:
        - bucket est une liste de la forme [[*coordoonées], indice de la liste de coordoonées],
        - x_limit est un réel,
        - strict est un booléen.
        Post-conditions : ...

        WARNING: La modification de la taille de la liste de coordoonées n'est pas
                 prise en charge par la fonction.
        WARNING: Le point à l'index courant est toujours itéré.
    """

    bucket_id = bucket[1]

    while bucket_id < len(bucket[0]) and \
        ((    strict and points[bucket[0][bucket_id]][0] <  x_limit) or \
         (not strict and points[bucket[0][bucket_id]][0] <= x_limit) or \
         current_index == bucket[0][bucket_id]):

        yield bucket[0][bucket_id]
        bucket_id += 1


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
            # -- Tests --
            tests   = defaultdict(lambda: defaultdict(lambda: 0))
            writing = defaultdict(lambda: 0)

            segments = {
                'tests': {
                    'circles'      : [],
                    'obs_isolates' : [],
                    'obs_groups'   : [],
                    'isolate_other': [],
                    'isolate_link' : []
                },
                'finals': {
                    'groups': []
                }
            }

            # -- Analyse --

            # Buckets

            # Un "bucket" est une liste des points sur un découpage de l'axe Y.
            # L'intersection entre "buckets" et vide.

            BUCKET_SIZE = distance / 2

            last_observed_id = 0
            buckets = {
                'groups'  : defaultdict(lambda: [[], 0]),
                'isolates': defaultdict(lambda: [[], 0])
            }

            # Groups

            # Le registre est la liste des correspondances (point, point référent).
            # groups est l'état partiel courant des groupes et results en est l'état final.

            register, groups, results = {}, {}, {}

            # Buffers
            near_groups = set() # Groupes pouvant être fusionné avec le point courant.
            removing_buffer = set() # Points pouvant être supprimé des points isolés.

            # Listes des points pouvant lier deux groupes grâces à des points isolés.
            # La clé étant le test "ordonné du point du groupe est inférieure à l'ordonné
            # du point courant".
            # (aside_y < current_y)
            isolates_links = {
                True : { 'in': set(), 'out': set() },
                False: { 'in': set(), 'out': set() }
            }

            points.sort()


        # x-------------x
        # |  Main loop  |
        # x-------------x

        for i, point in enumerate(points):

            if i not in register:

                # x------------------x
                # |  Initialization  |
                # x------------------x

                with Perf(2):

                    # Components
                    x, y = point
                    bucket_id = floor(y / BUCKET_SIZE)

                    # Clear buffers
                    near_groups.clear()
                    near_groups.add(i)

                    for side in isolates_links.values():
                        for category in side.values():
                            category.clear()

                    # Groups
                    groups[i] = set([i])
                    register[i] = i


                # x----------x
                # |  Groups  |
                # x----------x

                with Perf(3):

                    # Observation des buckets à une distance de plus ou moins 4 du bucket courant
                    for aside_bucket_id in range(max(bucket_id - 4, 0), bucket_id + 4 + 1):
                        bucket = buckets['groups'][aside_bucket_id]

                        # Suppression des points ne pouvant pas passer les tests
                        # (n'apportant aucune information)
                        for aside_id in iter_bucket(points, bucket, i, x - distance, True):
                            groups[register[aside_id]].remove(aside_id)

                            bucket[1] += 1

                        # Efficient
                        for aside_id in iter_bucket(points, bucket, i, x + distance):

                            if register[aside_id] not in near_groups:

                                point_y = points[aside_id][1]

                                if is_at_distance(point, points[aside_id], distance):
                                    # In distance circle

                                    near_groups.add(register[aside_id])

                                    if aside_id in isolates_links[point_y < y]['out']:
                                        isolates_links[point_y < y]['out'].remove(aside_id)

                                    segments['finals']['groups'].append((point, points[aside_id]))

                                elif is_at_distance(points[aside_id], (x, y + ((point_y >= y) * 2 - 1) * distance), distance):
                                    # In double distance circle

                                    isolates_links[point_y < y]['out'].add(aside_id)

                                tests[i][aside_id] += 1
                                segments['tests']['obs_groups'].append((point, points[aside_id]))


                # x------------x
                # |  Isolates  |
                # x------------x

                with Perf(4):

                    # News
                    while last_observed_id < len(points) and points[last_observed_id][0] <= x + distance:
                        buckets['isolates'][floor(points[last_observed_id][1] // BUCKET_SIZE)][0].append(last_observed_id)

                        last_observed_id += 1

                    # Observed

                    # Observation des buckets à une distance de plus ou moins 2 du bucket courant
                    for aside_bucket_id in range(max(bucket_id - 2, 0), bucket_id + 2 + 1):
                        bucket = buckets['isolates'][aside_bucket_id]

                        # Suppression des points ne pouvant pas passer les tests (n'apportant aucune information)
                        for _ in iter_bucket(points, bucket, i, x, True):
                            bucket[1] += 1

                        # Efficient
                        removing_buffer.clear()

                        for aside_id in iter_bucket(points, bucket, i, x + distance):
                            point_y = points[aside_id][1]

                            if is_at_distance(point, points[aside_id], distance):
                                # In distance circle

                                groups[i].add(aside_id)
                                register[aside_id] = i

                                if is_at_distance(points[aside_id], (x, y + ((point_y > y) * 2 - 1) * distance), distance):
                                    isolates_links[point_y < y]['in'].add(aside_id)

                                buckets['groups'][floor(point_y // BUCKET_SIZE)][0].append(aside_id)
                                removing_buffer.add(aside_id)

                                segments['finals']['groups'].append((point, points[aside_id]))

                            # Tests
                            tests[i][aside_id] += 1
                            segments['tests']['obs_isolates'].append((point, points[aside_id]))

                        for aside_id in removing_buffer:
                            bucket[0].remove(aside_id)


                # x--------------------x
                # |  Isolates's links  |
                # x--------------------x

                with Perf(6):

                    # Boucle sur les possibilités observés jusqu'à en trouver au maximum
                    # une inférieure et une supérieure.

                    for in_points in isolates_links.values():

                        for k, j in product(in_points['in'], in_points['out']):

                            tests[k][j] += 1
                            segments['tests']['isolate_link'].append((points[k], points[j]))

                            if is_at_distance(points[j], points[k], distance):
                                # In distance circle

                                near_groups.add(register[j])

                                segments['finals']['groups'].append((points[j], points[k]))
                                break


                # x-----------x
                # |  Fusions  |
                # x-----------x

                with Perf(7):
                    # Recherche du plus grand groupe
                    max_group_id, max_count = i, len(groups[i])

                    for group_id in near_groups:
                        if len(groups[group_id]) > max_count:
                            max_group_id, max_count = group_id, len(groups[group_id])

                    near_groups.remove(max_group_id)

                    # Ajout d'un résultat
                    results[i] = set()
                    results[i].update(groups[i])

                    # Mise à jour du registre
                    for group_id in near_groups:
                        groups[max_group_id].update(groups[group_id])
                        results[max_group_id].update(results[group_id])

                        results.pop(group_id)

                        for point_id in groups[group_id]:
                            register[point_id] = max_group_id

                        register[group_id] = max_group_id

                        writing[max_group_id] += 1


                circle = [(distance * cos(c*pi/10) + x, distance * sin(c*pi/10) + y) for c in range(20)]
                for point_1, point_2 in zip(circle, islice(cycle(circle), 1, None)):
                    segments['tests']['circles'].append((point_1, point_2))


        # Calcul du résultat
        counts = list((len(group) for group in results.values()))
        counts.sort(reverse=True)

        print('\n  ', counts, sep='', end='\n')


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
    if len(points) <= 45:
        for j, i in table(len(points), len(points)):

            if i == j:
                print(set_color('--', 'red'), end='')

            elif tests[i][j] > 0:
                color = 'yellow'  if tests[j][i] > 0 else \
                        'magenta' if tests[i][j] > 1 else 'white'

                print(set_color(f"{tests[i][j]:2}", color), end='')
            else:
                print("  ", end='')

    total = 0
    for line in tests.values():
        for count in line.values():
            total += count

    print(f"  Total des comparaisons : {total} ({total * 100 / (len(points) * len(points)):.5f}%)", '\n')


    # -- Performances --
    percent = 100 / Perf.times[0]

    print('  Performances :')

    print("  x----------x----------------x----------x")
    print("  | Total    | Sections       | Percents |")
    print("  x----------x----------------x----------x")
    print(f"  |          | Initialization |   {(Perf.times[1] * percent):5.2f}% |")
    print("  |          x----------------x----------x")
    print(f"  |          | Initialization |   {(Perf.times[2] * percent):5.2f}% |")
    print(f"  | {Perf.times[0]:8.5f} | Groups         |   {(Perf.times[3] * percent):5.2f}% |")
    print(f"  |          | Isolates       |   {(Perf.times[4] * percent):5.2f}% |")
    print(f"  |          | Links          |   {(Perf.times[6] * percent):5.2f}% |")
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
