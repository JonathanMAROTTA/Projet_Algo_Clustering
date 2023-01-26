#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from math import cos, sin, pi
from timeit import timeit
from sys import argv
from itertools import islice, cycle

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

    last_efficient_x = 0
    groups, register = {}, {}

    for i, point in enumerate(points):
        if i not in register.keys():
            x, y = point.coordinates

            # Search last efficient index
            while last_efficient_x < len(points) and points[last_efficient_x].coordinates[0] <= x - distance:
                last_efficient_x += 1

            # Create new group
            groups[i] = set([i])
            register[i] = i

            j = last_efficient_x
            while j < len(points) and points[j].coordinates[0] <= x + distance:
                aside_x, aside_y = points[j].coordinates

                if y - distance <= aside_y <= y + distance and point.distance_to(points[j]) <= distance:
                    if j in register.keys() and i not in groups[register[j]]:
                        aside_group_id = register[j]
                        aside_group = groups[aside_group_id]

                        current_group_id = register[i]

                        # Réasignation des groupes
                        for point_id in groups[current_group_id]:
                            register[point_id] = aside_group_id
                            aside_group.add(point_id)

                        del groups[current_group_id]

                    register[j] = register[i]
                    groups[register[i]].add(j)

                j += 1

    result = list(len(group) for group in groups.values())
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
