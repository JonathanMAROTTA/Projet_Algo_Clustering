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

    points_calc = list([point, None] for point in points)
    counts = {}
    terminals = set()

    circles = []
    segments = []
    for i in range(len(points_calc)):
        point = points_calc[i][0]

        if points_calc[i][1] is None:
            points_calc[i][1] = i
            terminals.add(i)

            count = 1

            j = 0
            while j < len(points_calc):
                if j != i:
                    if points_calc[j][1] is None:
                        if point.distance_to(points_calc[j][0]) <= distance:
                            points_calc[j][1] = i
                            segments.append(Segment([point, points_calc[j][0]]))
                            count += 1
                    else:
                        if point.distance_to(points_calc[j][0]) <= distance:
                            count += counts[points_calc[j][1]]
                            segments.append(Segment([point, points_calc[j][0]]))
                            terminals.remove(points_calc[j][1])

                j += 1

            counts[i] = count

            cercle = [Point([distance * cos(c*pi/10), distance * sin(c*pi/10)]) + point for c in range(20)]
            circles.append(cercle)

            segments.append((
                Segment([p1, p2])
                for p1, p2 in zip(cercle, islice(cycle(cercle), 1, None))
            ))

    result = []
    for group in terminals:
        result.append(counts[group])

    tycat(points, *segments)

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
