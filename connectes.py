#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from math import cos, sin, pi
from timeit import timeit
from sys import argv
from itertools import islice, cycle
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

def remove_inefficients(points, observed, base_id, x, case_y, distance):
    # Groups
    if case_y not in observed['groups']:
        observed['groups'][case_y] = [[], 0]
    else:
        obs_points, i = observed['groups'][case_y]

        while i < len(obs_points) and (points[obs_points[i]].coordinates[0] < x - distance or base_id == obs_points[i]):
            i += 1

        observed['groups'][case_y][1] = i

    # Isolates
    if case_y not in observed['isolates']:
        observed['isolates'][case_y] = [[], 0]
    else:
        obs_points, i = observed['isolates'][case_y]

        while i < len(obs_points) and (points[obs_points[i]].coordinates[0] < x or base_id == obs_points[i]):
            i += 1

        observed['isolates'][case_y][1] = i

def run_clusters(observed, case_y):
    for translation in range(-1, 2):
        yield translation, observed['isolates'][case_y + translation], observed['groups'][case_y + translation]

# A voir
def run_clusters_points(observed, case_y, key):
    for translation in range(-1, 2):
        cluster_points, i = observed[key][case_y + translation]

        while i < len(cluster_points):
            next_i = i + 1

            yield cluster_points[i]

            i = next_i

def print_components_sizes(distance, points):
    """
    affichage des tailles triees de chaque composante
    """
    # x------------------x
    # |  Initialization  |
    # x------------------x

    # -- Tests --
    with perf(0) as _:
        tests   = [[0 for _ in range(len(points))] for _ in range(len(points))]
        writing =  [0 for _ in points]

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

        # -- Graph --
        groups, group_result = {}, set()
        
        observed = {
            'groups'  : {},
            'isolates': {}
        }
        last_observed_id = 0
        old_groups_boundaries = {}

        group_buffer = set()

        # Dictonary's key is the boolean : j.y < j.y
        isolates_links = {
            True : { 'in': set(), 'out': set() },
            False: { 'in': set(), 'out': set() }
        }

        points.sort()

        for i, point in enumerate(points):

            if i not in groups.keys():

                # x------------------x
                # |  Initialization  |
                # x------------------x

                with perf(1) as _:
                    x, y = point.coordinates
                    groups[i] = set([i])

                    # Clear buffers
                    group_buffer.clear()

                    for side in isolates_links.values():
                        for category in side.values():
                            category.clear()

                    # Remove inefficients
                    case_y = math.floor(y / distance)

                    for translation in range(-1, 2):
                        remove_inefficients(points, observed, i, x, case_y + translation, distance)
                        old_groups_boundaries[translation] = len(observed['groups'][case_y + translation][0])


                # x------------x
                # |  Isolates  |
                # x------------x

                with perf(2) as _:

                    # Clusters
                    for _, isolates_cluster, group_cluster in run_clusters(observed, case_y):
                        isolates_points, isolate_id = isolates_cluster

                        while isolate_id < len(isolates_points):
                            j = isolates_points[isolate_id]
                            isolate_x, isolate_y = points[j].coordinates

                            if y - distance <= isolate_y <= y + distance and point.distance_to(points[j]) <= distance:
                                # In distance circle

                                groups[j] = groups[i]
                                groups[i].add(j)

                                group_cluster[0].append(j)
                                isolates_links[isolate_y < y]['in'].add(j)

                                del isolates_points[isolate_id]

                                segments['finals']['groups'].append((i, j))
                            else:
                                # Out distance circle

                                isolate_id += 1

                            # Tests
                            tests[i][j] += 1
                            segments['tests']['obs_isolates'].append((i, j))

                    # Outside clusters
                    obs_updates = []

                    while last_observed_id < len(points) and points[last_observed_id].coordinates[0] <= x + distance:
                        j = last_observed_id
                        new_x, new_y = points[j].coordinates
                        case_new_y = math.floor(new_y / distance)
                        
                        if case_new_y not in observed['groups']:
                            observed['groups'][case_new_y] = [[], 0]

                        obs_groups = observed['groups'][case_new_y][0]

                        if y - distance <= new_y <= y + distance and point.distance_to(points[j]) <= distance:
                            # In distance circle

                            groups[j] = groups[i]
                            groups[i].add(j)

                            obs_groups.append(j)
                            isolates_links[new_y < y]['in'].add(j)

                            obs_updates.append(case_new_y)

                            segments['finals']['groups'].append((i, j))
                        elif j not in obs_groups: # A voir
                            # Out distance circle

                            if case_new_y not in observed['isolates'].keys():
                                observed['isolates'][case_new_y] = [[j], 0]
                            else:
                                observed['isolates'][case_new_y][0].append(j)

                        tests[i][j] += 1
                        segments['tests']['isolate_other'].append((i, j))

                        last_observed_id += 1

                    # Sort only obs_groups updated
                    for update_case in obs_updates:
                        observed['groups'][update_case][0].sort()


                # x----------x
                # |  Groups  |
                # x----------x

                with perf(3) as _:
                    max_grp_count, max_grp_id = 1, i

                    # Clusters
                    with perf(4) as _:
                        for translation, isolates_cluster, group_cluster in run_clusters(observed, case_y):
                            groups_points, groups_id = group_cluster

                            while groups_id < old_groups_boundaries[translation] and points[groups_points[groups_id]].coordinates[0] <= x + distance:

                                j = groups_points[groups_id]
                                grp_x, grp_y = points[j].coordinates

                                if j not in groups[i] and j not in groups[max_grp_id] and j not in group_buffer:

                                    if y - distance <= grp_y <= y + distance and point.distance_to(points[j]) <= distance:
                                        # In distance circle

                                        grp_count = len(groups[j])
                                        if grp_count > max_grp_count:
                                            group_buffer.update(groups[max_grp_id])

                                            max_grp_id, max_grp_count = j, grp_count
                                        else:
                                            group_buffer.update(groups[j])

                                        segments['finals']['groups'].append((i, j))

                                    elif y - 2 * distance <= grp_y < y or y < grp_y <= y + 2 * distance:
                                        # In double distance circle

                                        isolates_links[grp_y < y]['out'].add(j)

                                    tests[i][j] += 1

                                    segments['tests']['obs_groups'].append((i, j))

                                groups_id += 1

                    # Isolates's links
                    with perf(5) as _:
                        for in_points in isolates_links.values():
                            in_points['out'].difference_update(groups[i])
                            
                            for j in in_points['in']:
                                for k in in_points['out']:

                                    tests[j][k] += 1
                                    segments['tests']['isolate_link'].append((j, k))

                                    if points[k].distance_to(points[j]) <= distance:                        
                                        # In distance circle

                                        grp_count = len(groups[k])
                                        if grp_count > max_grp_count:
                                            group_buffer.update(groups[max_grp_id])

                                            max_grp_id, max_grp_count = k, grp_count
                                        else:
                                            group_buffer.update(groups[k])

                                        segments['finals']['groups'].append((j, k))
                                        break

                    # Fusions
                    with perf(6):

                        if len(group_buffer) > 0:
                            for k in group_buffer:
                                groups[k] = groups[max_grp_id]
                                writing[k] += 1

                            groups[i] = groups[max_grp_id]
                            groups[i].update(group_buffer)

                            group_result.difference_update(groups[max_grp_id])       
                            group_result.add(max_grp_id)
                        else:
                            group_result.add(i)
                
                #cercle = [Point([distance * cos(c*pi/10), distance * sin(c*pi/10)]) + point for c in range(20)]
                #segments['circles'].append([(p1, p2) for p1, p2 in zip(cercle, islice(cycle(cercle), 1, None))])


        result = list((len(groups[group_id]) for group_id in group_result))
        result.sort(reverse=True)

        print('\n  ', result, sep='', end='\n')


    # x---------x
    # |  Tests  |
    # x---------x

    make_test = True, False, False, True

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
                        'gray'    if tests[i][j] > 1 and j in groups[i] else \
                        'green'   if j in groups[i] else \
                        'magenta' if tests[i][j] > 1 else 'white'

                print(set_color(f"{tests[i][j]:2}", color), end='')
            else:
                print(f"  ", end='')

        print(f"  Total des comparaisons : {total} ({total * 100 / (len(points) * len(points)):.2f}%)", '\n')
    else:
        total = 0

        for i in range(len(points)):
            for j in range(len(points)):
                total += tests[i][j]

        print(f"  Total des comparaisons : {total} ({total * 100 / (len(points) * len(points)):.2f}%)", '\n')

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

    # Perfs
    if make_test[3]:
        percent = 100 / perf.times[0]

        print(f"  Performances")
        print(f"  - Total : {perf.times[0]:.5f} secondes")
        print(f"  - Initialisation : {(perf.times[1] * percent):.2f}%")
        print(f"  - Isolés : {(perf.times[2] * percent):.2f}%")
        print(f"  - Groupes : {(perf.times[3] * percent):.2f}%")
        print(f"    * Liens entre groupes: {(perf.times[4] * 100 / perf.times[3]):.2f}%")
        print(f"    * Liens entre isolés: {(perf.times[5] * 100 / perf.times[3]):.2f}%")
        print(f"    * Réécriture: {(perf.times[6] * 100 / perf.times[3]):.2f}%")
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
