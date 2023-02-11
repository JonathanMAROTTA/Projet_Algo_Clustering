#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from sys import argv
from itertools import product
from collections import defaultdict
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

                        elif test_2D_distance_coordinates(points[j].coordinates, (x, y + ((point_y >= y) * 2 - 1) * distance), distance):
                            # In double distance circle

                            isolates_links[point_y < y]['out'].add(j)

                    point_id += 1

            # Isolates
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
                    else:
                        # Out distance circle

                        point_id += 1

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
                    else:
                        # Out distance circle

                        point_id += 1
                        
            # News
            while last_observed_id < len(points) and points[last_observed_id].coordinates[0] < x:
                point_x, point_y = points[last_observed_id].coordinates

                if test_2D_distance(point, points[j], distance):
                    # In distance circle

                    groups[i].add(last_observed_id)
                    register[last_observed_id] = i

                    observed['groups'][get_cluster_id(point_y, distance)][0].append(last_observed_id)
                else:
                    # Out distance circle

                    observed['isolates'][get_cluster_id(point_y, distance)][0].append(last_observed_id)

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
                else:
                    # Out distance circle

                    observed['isolates'][get_cluster_id(point_y, distance)][0].append(last_observed_id)

                last_observed_id += 1


            # x----------x
            # |  Groups  |
            # x----------x

            # Isolates's links
            for in_points in isolates_links.values():

                for k, j in product(in_points['in'], in_points['out']):

                    if test_2D_distance(points[j], points[k], distance):
                        # In distance circle

                        near_groups.add(register[j])
                        break

            # Fusions
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


    result = list((len(group) for group in groups_result.values()))
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
