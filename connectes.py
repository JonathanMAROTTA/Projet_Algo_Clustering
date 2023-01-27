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

def print_components_sizes(distance, points):
    """
    affichage des tailles triees de chaque composante
    """
    start = perf_counter()

    points.sort()

    groups, result_ids = {}, set()

    pts2, seg1, seg2, nb_comparaison, cmp = [], [], [], 0, [0,0]

    for i, point in enumerate(points):
        nb_comparaison += 1
        if i not in groups.keys():
            cmp[0] += 1
            x, y = point.coordinates

            # Create new group
            groups[i] = set([i])
            result_ids.add(i)

            for direction in [-1,1]:
                j = i + direction
                while 0 <= j < len(points) and x - distance <= points[j].coordinates[0] <= x + distance:
                    nb_comparaison += 1
                    
                    nb_comparaison += 1
                    if y - distance <= points[j].coordinates[1] <= y + distance and point.distance_to(points[j]) <= distance:
                        nb_comparaison += 1
                        if j in groups.keys() and i not in groups[j]:
                            groups[i].update(groups[j])

                            current_group_ids = groups[j]
                            for k in current_group_ids:
                                groups[k] = groups[i]

                                if k in result_ids:
                                    result_ids.remove(k)
                        else:
                            groups[j] = groups[i]
                            groups[i].add(j)

                        seg1.append(Segment([point, points[j]]))
        
                    seg2.append(Segment([point, points[j]]))
                    cmp[1] += 1
                    j += direction

                pts2.append(point)
                cercle = [Point([distance * cos(c*pi/10), distance * sin(c*pi/10)]) + point for c in range(20)]
                seg2.append((Segment([p1, p2]) for p1, p2 in zip(cercle, islice(cycle(cercle), 1, None))))


    # Display
    print('Comparaison de point :', nb_comparaison)
    tycat(points, *seg2)

    # Display
    tycat(points, *seg1)

    result = list((len(groups[group_id]) for group_id in result_ids))
    result.sort(reverse=True)

    print(result)

    end = perf_counter()
    print(f"Performance : {end - start:.5f}")
    print("Nombre de points :",len(points))
    print("Comparaison / point :", cmp[1] / cmp[0])


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
