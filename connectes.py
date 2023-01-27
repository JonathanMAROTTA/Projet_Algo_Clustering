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

    groups = {}

    for i, point in enumerate(points):

        if i not in groups.keys():
            x, y = point.coordinates

            # Create new group
            groups[i] = set([i])

            for direction in [-1,1]:
                j = i + direction
                while 0 <= j < len(points) and x - distance <= points[j].coordinates[0] <= x + distance:

                    if y - distance <= points[j].coordinates[1] <= y + distance and point.distance_to(points[j]) <= distance:

                        if j in groups.keys() and i not in groups[j]:
                            groups[i].update(groups[j])

                            current_group_ids = groups[j]
                            for k in current_group_ids:
                                groups[k] = groups[i]
                        else:
                            groups[j] = groups[i]
                            groups[i].add(j)

                    j += direction


    result = list((len(group) for group in (set((frozenset(group) for group in groups.values())))))
    result.sort(reverse=True)

    print(result)

    end = perf_counter()
    print(f"Performance : {end - start:.5f}")


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
