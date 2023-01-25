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


def comparaison_generator(points, groups, register, distance):
    last_efficient_x, group_next_id = 0, 0
    segments, points_comparaison = [], 0

    for i, point in enumerate(points):
        if i not in register.keys():
            x, y = point.coordinates

            # Search last efficient index
            while last_efficient_x < len(points) and points[last_efficient_x].coordinates[0] <= x - distance:
                last_efficient_x += 1

            # Create new group
            groups[group_next_id] = set([i])
            register[i] = group_next_id

            group_next_id += 1

            j = last_efficient_x
            while j < len(points) and points[j].coordinates[0] <= x + distance:
                if j != i and y - distance <= points[j].coordinates[1] <= y + distance:
                    points_comparaison += 1
                    if point.distance_to(points[j]) <= distance: 
                        
                        yield i, j, point, points[j]

                    segments.append(Segment([point, points[j]]))
                j += 1

    # Display
    print('Comparaison de point :', points_comparaison)
    tycat(points, *segments)

def print_components_sizes(distance, points):
    """
    affichage des tailles triees de chaque composante
    """
    points.sort()

    groups, register = {}, {}

    circles, segments = [], []

    for current_id, aside_id, point, aside in comparaison_generator(points, groups, register, distance):
        if aside_id in register.keys() and current_id not in groups[register[aside_id]]:
            aside_group_id = register[aside_id]
            aside_group = groups[aside_group_id]

            current_group_id = register[current_id]

            # Réasignation des groupes
            for point_id in groups[current_group_id]:
                register[point_id] = aside_group_id
                aside_group.add(point_id)

            del groups[current_group_id]

        register[aside_id] = register[current_id]
        groups[register[current_id]].add(aside_id)

        segments.append(Segment([point, aside]))

        #cercle = [Point([distance * cos(c*pi/10), distance * sin(c*pi/10)]) + point for c in range(20)]
        #circles.append(cercle)

        #segments.append((Segment([p1, p2]) for p1, p2 in zip(cercle, islice(cycle(cercle), 1, None))))

    # Display
    tycat(points, *segments)

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
