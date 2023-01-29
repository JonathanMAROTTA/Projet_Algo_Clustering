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
    points.sort()

    groups, result_ids = {}, set()
    grouped, isolated = [], []

    for i, point in enumerate(points):

        if i not in groups.keys():
            x, y = point.coordinates

            # Remove inefficient
            while len(grouped) > 0 and points[grouped[0]].coordinates[0] < x - distance:
                del grouped[0]
            while len(isolated) > 0 and points[isolated[0]].coordinates[0] < x:
                del isolated[0]

            # Look at grouped
            groups[i] = set([])

            for point_id in grouped:

                if point_id not in groups[i] and point.distance_to(points[point_id]) <= distance:
                    groups[i].update(groups[point_id])

            for k in groups[i]:
                groups[k] = groups[i]

                if k in result_ids:
                    result_ids.remove(k)

            groups[i].add(i)
            result_ids.add(i)

            # Look at isolated
            j = 0
            while j < len(isolated):

                if point.distance_to(points[isolated[j]]) <= distance:
                    groups[isolated[j]] = groups[i]

                    groups[i].add(isolated[j])

                    grouped.append(isolated[j])
                    del isolated[j]
                else:
                    j += 1

            # Look at new
            j = isolated[-1] + 1 if len(isolated) > 0 else i + 1
            while j < len(points) and points[j].coordinates[0] <= x + distance:

                if point.distance_to(points[j]) <= distance:
                    groups[j] = groups[i]
                    groups[i].add(j)

                    grouped.append(j)
                else:
                    isolated.append(j)

                j += 1

    result = list((len(groups[group_id]) for group_id in result_ids))
    result.sort(reverse=True)

    print(result)
    

def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
