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

def print_components_sizes(distance, points):
    """
    affichage des tailles triees de chaque composante
    """
    start = perf_counter()
    perf_stats = [0,0,0,0,0,0]
    
    # Tests's list
    tests = [[0 for _ in range(len(points))] for _ in range(len(points))]
    writing = [0 for _ in points]

    points.sort()

    groups, group_result = {}, set()
    
    obs_groups  , obs_groups_idx   = [], 0 
    obs_isolates, obs_isolates_idx = [], 0

    group_buffer = set()

    # Dictonary's key is the boolean : j.y < j.y
    isolates_links = {
        True : { 'near': set(), 'far': set() },
        False: { 'near': set(), 'far': set() }
    }

    pts2, seg1, seg2 = [], [], []

    for i, point in enumerate(points):

        if i not in groups.keys():

            # x------------------x
            # |  Initialization  |
            # x------------------x

            time = perf_counter()

            x, y = point.coordinates
            groups[i] = set([i])

            # Clear buffers
            group_buffer .clear()

            isolates_links[True ]['near'].clear()
            isolates_links[True ]['far' ].clear()
            isolates_links[False]['near'].clear()
            isolates_links[False]['far' ].clear()

            # Remove inefficients
            while obs_groups_idx   < len(obs_groups  ) and points[obs_groups  [obs_groups_idx  ]].coordinates[0] < x - distance:
                obs_groups_idx   += 1
            while obs_isolates_idx < len(obs_isolates) and points[obs_isolates[obs_isolates_idx]].coordinates[0] <= x:
                obs_isolates_idx += 1

            perf_stats[0] += perf_counter() - time

            # Boundaries
            old_groups_boundary = len(obs_groups)


            # x------------x
            # |  Isolates  |
            # x------------x

            time = perf_counter()

            # Observations
            isolate_id = obs_isolates_idx
            while isolate_id < len(obs_isolates):
                j = obs_isolates[isolate_id]

                #seg2.append(Segment([point, points[j]]))
                tests[i][j] += 1

                isolate_y = points[j].coordinates[1]

                if y - distance <= isolate_y <= y + distance and point.distance_to(points[j]) <= distance:
                    groups[j] = groups[i]
                    groups[i].add(j)

                    obs_groups.append(j)
                    isolates_links[isolate_y < y]['near'].add(j)

                    del obs_isolates[isolate_id]

                    seg1.append(Segment([point, points[j]]))
                    #seg2.append(Segment([point, points[j]]))

                isolate_id += 1

            # Others
            j = obs_isolates[-1] + 1        if obs_isolates_idx < len(obs_isolates) else i + 1
            j = max(j, obs_groups[-1] + 1)  if obs_groups_idx   < len(obs_groups  ) else j

            while j < len(points) and points[j].coordinates[0] <= x + distance:
                new_y = points[j].coordinates[1]
                
                if y - distance <= new_y <= y + distance and point.distance_to(points[j]) <= distance:
                    groups[j] = groups[i]
                    groups[i].add(j)

                    seg1.append(Segment([point, points[j]]))

                    obs_groups.append(j)
                    isolates_links[new_y < y]['near'].add(j)

                    #seg2.append(Segment([point, points[j]]))
                elif j not in obs_groups:
                    obs_isolates.append(j)

                tests[i][j] += 1
                seg2.append(Segment([point, points[j]]))
                j += 1

            obs_groups.sort()

            perf_stats[1] += perf_counter() - time


            # x----------x
            # |  Groups  |
            # x----------x

            time = perf_counter()

            max_grp_count, max_grp_id = 1, i

            # Observations
            time2 = perf_counter()

            grp_id = obs_groups_idx
            while grp_id < old_groups_boundary and points[obs_groups[grp_id]].coordinates[0] <= x + distance:

                j = obs_groups[grp_id]
                grp_x, grp_y = points[j].coordinates

                if j not in groups[i] and j not in groups[max_grp_id] and j not in group_buffer:

                    tests[i][j] += 1

                    if y - distance <= grp_y <= y + distance and point.distance_to(points[j]) <= distance:

                        grp_count = len(groups[j])
                        if grp_count > max_grp_count:
                            group_buffer.update(groups[max_grp_id])

                            max_grp_id, max_grp_count = j, grp_count
                        else:
                            group_buffer.update(groups[j])

                        seg1.append(Segment([point, points[j]]))

                    elif y - 2 * distance <= grp_y < y or y < grp_y <= y + 2 * distance:
                        isolates_links[grp_y < y]['far'].add(j)
                        #seg2.append(Segment([point, points[j]]))

                    seg2.append(Segment([point, points[j]]))
                grp_id += 1

            perf_stats[3] += perf_counter() - time2

            # Isolates's links
            time3 = perf_counter()
            
            for near_points in isolates_links.values():
                near_points['far'].difference_update(groups[i])
                
                for j in near_points['near']:
                    for k in near_points['far']:

                        tests[j][k] += 1
                        seg2.append(Segment([points[k], points[j]]))

                        if points[k].distance_to(points[j]) <= distance:                        

                            grp_count = len(groups[k])
                            if grp_count > max_grp_count:
                                group_buffer.update(groups[max_grp_id])

                                max_grp_id, max_grp_count = k, grp_count
                            else:
                                group_buffer.update(groups[k])

                            seg1.append(Segment([points[j], points[k]]))
                            break

            perf_stats[4] += perf_counter() - time3

            # Fusions
            time4 = perf_counter()

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

            perf_stats[5] += perf_counter() - time4

            perf_stats[2] += perf_counter() - time
            

            pts2.append(point)
            cercle = [Point([distance * cos(c*pi/10), distance * sin(c*pi/10)]) + point for c in range(20)]
            seg2.append((Segment([p1, p2]) for p1, p2 in zip(cercle, islice(cycle(cercle), 1, None))))
        #seg1.append((Segment([p1, p2]) for p1, p2 in zip(cercle, islice(cycle(cercle), 1, None))))

    result = list((len(groups[group_id]) for group_id in group_result))
    result.sort(reverse=True)

    print('\n  ', result, sep='', end='\n')

    delta = perf_counter() - start
    percent = 100 / delta

    print(f"\n  Performances")
    print(f"  - Total : {delta:.5f} secondes")
    print(f"  - Initialisation : {(perf_stats[0] * percent):.2f}%")
    print(f"  - Isolés : {(perf_stats[1] * percent):.2f}%")
    print(f"  - Groupes : {(perf_stats[2] * percent):.2f}%")
    print(f"    * Liens entre groupes: {(perf_stats[3] * 100 / perf_stats[2]):.2f}%")
    print(f"    * Liens entre isolés: {(perf_stats[4] * 100 / perf_stats[2]):.2f}%")
    print(f"    * Réécriture: {(perf_stats[5] * 100 / perf_stats[2]):.2f}%")
    print("  Nombre de points :",len(points), end='\n\n')

    # Display
    make_test = False

    if make_test:
        tycat(pts2, *seg2)
        tycat(points, *seg1)

        print('\n  ', result, sep='', end='\n\n')

        # x---------x
        # |  Tests  |
        # x---------x

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

        print('\n  Total :', total, f"({total * 100 / (len(points) * len(points)):.2f}%)", '\n')

        # Écritures
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


        print('\n  Total :', total, '\n')
        print('  ', result, sep='', end='\n\n')


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
