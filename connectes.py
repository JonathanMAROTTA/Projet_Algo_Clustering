#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from math import cos, sin, pi
from timeit import timeit
from sys import argv
from itertools import islice, cycle, product
from collections import defaultdict
from time import perf_counter
import math

from geo.tycat import tycat
from geo.point import Point
from geo.segment import Segment


def load_instance(filename):
    """
    loads .pts file.
    returns distance limit and points.
    """
    with open(filename, "r") as instance_file:
        lines = iter(instance_file)
        distance = float(next(lines))
        points = [Point([float(f) for f in l.split(",")]) for l in lines]

    return distance, points

# -- Fonctions tests --
# Perfs
class perf():
    times = {}

    def __init__(self, index):
        if index not in perf.times:
            perf.times[index] = 0

        self.index = index
        self.start = 0

    def __enter__(self):
        self.start = perf_counter()

        return self

    def __exit__(self, type, value, traceback):
        perf.times[self.index] += perf_counter() - self.start


# Tables
def separation(*sizes):
    print('  ', end='')

    for config in sizes:
        for _ in range(config[1]):
            print('-' * config[0], 'x', sep='', end='')
    print('')
def head(size, *others):
    print('     |', end='')

    for i in range(size):
        print(f" {i:2} |", end="")

    for name in others:
        print(f" {name} |", end='')
    print('')
def set_color(text, color):
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
    head(x_length)
    separation((3, 1), (4, x_length))

    for y in range(y_length):
        print(f"  {y:2} | ", end='') 

        for x in range(x_length):
            yield x, y

            print(f" | ", end='')

        print('')

        separation((3, 1), (4, x_length))

# ---------------------

def get_cluster_id(y, distance):
    return math.floor(2 * y / distance)

def run_clusters(cluster_id, relative_min, relative_max):

    for aside_cluster_id in range(max(cluster_id + relative_min, 0), cluster_id + relative_max + 1):
        
        yield aside_cluster_id

def test_2D_distance_coordinates(pos1, pos2, distance):
    dx, dy = pos2[0] - pos1[0], pos2[1] - pos1[1]
    return dx*dx + dy*dy <= distance * distance

def test_2D_distance(point1, point2, distance):
    dx, dy = point2.coordinates[0] - point1.coordinates[0], point2.coordinates[1] - point1.coordinates[1]
    return dx*dx + dy*dy <= distance * distance


def print_components_sizes(distance, points):
    """
    affichage des tailles triees de chaque composante
    """
    # x------------------x
    # |  Initialization  |
    # x------------------x

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

    with perf(0):

        with perf(7):
            # -- Graph --
            register, groups, groups_result = {}, {}, {}
            near_groups = set()

            observed = { 'groups': defaultdict(lambda: [[], 0]), 'isolates': defaultdict(lambda: [[], 0]) }
            last_observed_id = 0

            # Dictonary's key is the boolean : j.y < j.y
            isolates_links = {
                True : { 'in': set(), 'out': set() },
                False: { 'in': set(), 'out': set() }
            }

            points.sort()

        for i, point in enumerate(points):

            if i not in register.keys():

                # x------------------x
                # |  Initialization  |
                # x------------------x
                
                with perf(1):
                    x, y = point.coordinates
                    cluster_id = get_cluster_id(y, distance)

                    # Clear buffers
                    near_groups.clear()
                    near_groups.add(i)

                    for side in isolates_links.values():
                        for category in side.values():
                            category.clear()

                    # Groups
                    groups[i] = set([i])
                    register[i] = i


                # x------------x
                # |  Clusters  |
                # x------------x

                # Groups
                with perf(3):

                    with perf(4):
                        for aside_cluster_id in range(max(cluster_id - 4, 0), cluster_id + 4 + 1):
                            cluster, point_id = observed['groups'][aside_cluster_id]

                            # Remove
                            while point_id < len(cluster) and (points[cluster[point_id]].coordinates[0] < x - distance or i == cluster[point_id]):

                                groups[register[cluster[point_id]]].remove(cluster[point_id])
                                del register[cluster[point_id]]

                                point_id += 1

                            observed['groups'][aside_cluster_id][1] = point_id

                            # Observe
                            while point_id < len(cluster):
                                j = cluster[point_id]

                                if register[j] not in near_groups:

                                    point_x, point_y = points[j].coordinates

                                    if test_2D_distance(point, points[j], distance):
                                        # In distance circle

                                        near_groups.add(register[j])

                                        if j in isolates_links[point_y < y]['out']:
                                            isolates_links[point_y < y]['out'].remove(j)

                                        segments['finals']['groups'].append((i, j))

                                    elif test_2D_distance_coordinates(points[j].coordinates, (x, y + ((point_y >= y) * 2 - 1) * distance), distance):
                                        # In double distance circle

                                        isolates_links[point_y < y]['out'].add(j)

                                    tests[i][j] += 1
                                    segments['tests']['obs_groups'].append((i, j))

                                point_id += 1

                # Isolates
                with perf(2):
                    for aside_cluster_id in range(max(cluster_id - 2, 0), cluster_id + 2 + 1):
                        cluster, point_id = observed['isolates'][aside_cluster_id]

                        # Remove
                        while point_id < len(cluster) and (points[cluster[point_id]].coordinates[0] < x or i == cluster[point_id]):
                            point_id += 1

                        observed['isolates'][aside_cluster_id][1] = point_id


                        # Observe
                        while point_id < len(cluster) and points[cluster[point_id]].coordinates[0] < x:
                            j = cluster[point_id]
                            point_x, point_y = points[j].coordinates

                            if test_2D_distance(point, points[j], distance):
                                # In distance circle

                                groups[i].add(j)
                                register[j] = i

                                observed['groups'][get_cluster_id(point_y, distance)][0].append(j)
                                del cluster[point_id]

                                segments['finals']['groups'].append((i, j))
                            else:
                                # Out distance circle

                                point_id += 1

                            # Tests
                            tests[i][j] += 1
                            segments['tests']['obs_isolates'].append((i, j))

                        while point_id < len(cluster):
                            j = cluster[point_id]
                            point_x, point_y = points[j].coordinates

                            if test_2D_distance(point, points[j], distance):
                                # In distance circle

                                groups[i].add(j)
                                register[j] = i

                                if test_2D_distance_coordinates(points[j].coordinates, (x, y + ((point_y > y) * 2 - 1) * distance), distance):
                                    isolates_links[point_y < y]['in'].add(j)

                                observed['groups'][get_cluster_id(point_y, distance)][0].append(j)
                                del cluster[point_id]

                                segments['finals']['groups'].append((i, j))
                            else:
                                # Out distance circle

                                point_id += 1

                            # Tests
                            tests[i][j] += 1
                            segments['tests']['obs_isolates'].append((i, j))

                # News
                while last_observed_id < len(points) and points[last_observed_id].coordinates[0] < x:
                    point_x, point_y = points[last_observed_id].coordinates

                    if test_2D_distance(point, points[j], distance):
                        # In distance circle

                        groups[i].add(last_observed_id)
                        register[last_observed_id] = i

                        observed['groups'][get_cluster_id(point_y, distance)][0].append(last_observed_id)

                        segments['finals']['groups'].append((i, last_observed_id))
                    else:
                        # Out distance circle

                        observed['isolates'][get_cluster_id(point_y, distance)][0].append(last_observed_id)

                    # Tests
                    tests[i][last_observed_id] += 1
                    segments['tests']['obs_isolates'].append((i, last_observed_id))

                    last_observed_id += 1

                while last_observed_id < len(points) and points[last_observed_id].coordinates[0] <= x + distance:
                    point_x, point_y = points[last_observed_id].coordinates

                    if test_2D_distance(point, points[last_observed_id], distance):
                        # In distance circle

                        groups[i].add(last_observed_id)
                        register[last_observed_id] = i

                        if test_2D_distance_coordinates(points[last_observed_id].coordinates, (x, y + ((point_y > y) * 2 - 1) * distance), distance):
                            isolates_links[point_y < y]['in'].add(last_observed_id)

                        observed['groups'][get_cluster_id(point_y, distance)][0].append(last_observed_id)

                        segments['finals']['groups'].append((i, last_observed_id))
                    else:
                        # Out distance circle

                        observed['isolates'][get_cluster_id(point_y, distance)][0].append(last_observed_id)

                    # Tests
                    tests[i][last_observed_id] += 1
                    segments['tests']['obs_isolates'].append((i, last_observed_id))

                    last_observed_id += 1


                # x----------x
                # |  Groups  |
                # x----------x

                with perf(3):

                    # Isolates's links
                    with perf(5):

                        for in_points in isolates_links.values():

                            for k, j in product(in_points['in'], in_points['out']):

                                tests[k][j] += 1
                                segments['tests']['isolate_link'].append((k, j))

                                if test_2D_distance(points[j], points[k], distance):
                                    # In distance circle

                                    near_groups.add(register[j])

                                    segments['finals']['groups'].append((j, k))
                                    break

                    # Fusions
                    with perf(6):

                        max_group_id, max_count = i, len(groups[i])

                        for group_id in near_groups:
                            if len(groups[group_id]) > max_count:
                                max_group_id, max_count = group_id, len(groups[group_id])

                        near_groups.remove(max_group_id)

                        groups_result[i] = set()
                        groups_result[i].update(groups[i]) # A voir

                        for group_id in near_groups:
                            groups[max_group_id].update(groups[group_id])
                            groups_result[max_group_id].update(groups_result[group_id])

                            if group_id in groups_result.keys():
                                del groups_result[group_id]
                    
                            for point_id in groups[group_id]:
                                register[point_id] = max_group_id

                            register[group_id] = max_group_id

                            writing[max_group_id] += 1
                
                #cercle = [Point([distance * cos(c*pi/10), distance * sin(c*pi/10)]) + point for c in range(20)]
                #segments['circles'].append([(p1, p2) for p1, p2 in zip(cercle, islice(cycle(cercle), 1, None))])

        result = list((len(group) for group in groups_result.values()))
        result.sort(reverse=True)

        print('\n  ', result, sep='', end='\n')


    # x---------x
    # |  Tests  |
    # x---------x

    make_test = False, False, False, True

    # Graphs
    if make_test[0]:
        for graph in segments.values():
            graph_segment = []

            for linked_segment in graph.values():
                graph_segment.append([Segment([points[i], points[j]]) for i, j in linked_segment])

            tycat(points, *graph_segment)

        print('')

    # Comparaisons
    if make_test[1]:
        total = 0

        for j, i in table(len(points), len(points)):

            total += tests[i][j]

            if i == j:
                print(set_color('--', 'red'), end='')

            elif tests[i][j] > 0:
                color = 'yellow'  if tests[j][i] > 0 else \
                        'magenta' if tests[i][j] > 1 else 'white'

                print(set_color(f"{tests[i][j]:2}", color), end='')
            else:
                print(f"  ", end='')

        print(f"  Total des comparaisons : {total} ({total * 100 / (len(points) * len(points)):.2f}%)", '\n')
    else:
        total = 0

        for i in tests.keys():
            for j in tests[i].keys():
                total += tests[i][j]

        print(f"  Total des comparaisons : {total} ({total * 100 / (len(points) * len(points)):.5f}%)", '\n')

    # Écritures
    if make_test[2]:
        print('')
        total = 0

        for decimal, step in table(10, len(points) // 10):
            idx = 10 * step + decimal

            if writing[idx] > 0:
                total += writing[idx]

                color = 'magenta' if writing[idx] >  7 else \
                    'red'     if writing[idx] >  5 else \
                    'yellow'  if writing[idx] >  1 else \
                    'green'   if writing[idx] == 1 else 'white'

                print(set_color(f"{writing[idx]:2}", color), end='')
            else:
                print('  ', end='')
 
        print(f"  Total des écritures : {total}", '\n')
    else:
        total = 0

        for i in writing.keys():
            total += writing[i]

        print(f"  Total des écritures : {total} ({total * 100 / len(points):.5f}%)", '\n')

    # Perfs
    if make_test[3]:
        percent = 100 / perf.times[0]

        print(f"  Performances")
        print(f"  - Total : {perf.times[0]:.5f} secondes")
        print(f"  - Initialisation : {(perf.times[7] * percent):.2f}%")
        print(f"  - Boucle :")
        print(f"    * Initialisation : {(perf.times[1] * percent):.2f}%")
        print(f"    * Isolés : {(perf.times[2] * percent):.2f}%")
        print(f"    * Groupes : {(perf.times[3] * percent):.2f}%")
        print(f"      * Basics : {(perf.times[4] * 100 / perf.times[3]):.2f}%")
        print(f"      * Doubles : {(perf.times[5] * 100 / perf.times[3]):.2f}%")
        print(f"      * Réécriture : {(perf.times[6] * 100 / perf.times[3]):.2f}%")
        print("  Nombre de points :",len(points), '\n')

    print('  ', result, '\n', sep='')

def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
