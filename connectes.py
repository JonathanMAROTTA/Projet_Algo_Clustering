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

    grouped_index, isolated_index = 0, 0

    current_group = set()

    for i, point in enumerate(points):

        has_been_grouped = i in groups.keys()
        x, y = point.coordinates

        # Remove inefficient
        while grouped_index < len(grouped) and points[grouped[grouped_index]].coordinates[0] < x - distance:
            grouped_index += 1

        # Look at grouped
        if not has_been_grouped:
            groups[i] = set([i])

        current_group.clear()
        max_group_count, max_group_id = len(groups[i]), i

        j = grouped_index
        while j < len(grouped) and points[grouped[j]].coordinates[0] <= x + (not has_been_grouped) * distance:
            point_id = grouped[j]

            if point_id not in groups[i] and y - distance <= points[point_id].coordinates[1] <= y + distance and point.distance_to(points[point_id]) <= distance:
                
                group_count = len(groups[point_id])
                if group_count > max_group_count:
                    current_group.update(groups[max_group_id])

                    max_group_id = point_id
                    max_group_count = group_count
                else:
                    current_group.update(groups[point_id])

            j += 1

        if max_group_count > 0:
            groups[i].add(i)

            for k in current_group:
                groups[k] = groups[max_group_id]

            groups[i] = groups[max_group_id]
            groups[i].update(current_group)

            result_ids.difference_update(groups[max_group_id])       
            result_ids.add(max_group_id)
        else:
            groups[i].add(i)
            result_ids.add(i)

        if not has_been_grouped:
            # Remove inefficient
            while isolated_index < len(isolated) and points[isolated[isolated_index]].coordinates[0] <= x:
                isolated_index += 1

            # Look at isolated
            j = isolated_index
            while j < len(isolated):

                if y - distance <= points[isolated[j]].coordinates[1] <= y + distance and point.distance_to(points[isolated[j]]) <= distance:
                    groups[isolated[j]] = groups[i]

                    groups[i].add(isolated[j])
                    grouped.append(isolated[j])
                    del isolated[j]
                else:
                    j += 1

            # Look at new
            j = isolated[-1] + 1 if isolated_index < len(isolated) else i + 1
            j = max(j, grouped[-1] + 1)  if grouped_index < len(grouped) else j
            while j < len(points) and points[j].coordinates[0] <= x + distance:
                
                if y - distance <= points[j].coordinates[1] <= y + distance and point.distance_to(points[j]) <= distance:
                    groups[j] = groups[i]
                    groups[i].add(j)

                    grouped.append(j)
                else:
                    isolated.append(j)

                j += 1
                
            grouped.sort()

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
