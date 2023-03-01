#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from sys import argv
from itertools import groupby
from collections import defaultdict
from time import perf_counter

from graph_multiprocessing import graph_multiprocessing


# x------------------x
# |  File Managment  |
# x------------------x

def load_instance(filename):
    """
    loads .pts file.
    returns distance limit and points.
    """
    with open(filename, "r", encoding="utf-8") as instance_file:
        lines = iter(instance_file)
        distance = float(next(lines))
        points = [tuple(float(f) for f in l.split(",")) for l in lines]

    return distance, points


# x----------x
# |  Points  |
# x----------x

def is_at_distance(point_1, point_2, distance):
    """
        Def: Retourne le booléen indiquant si la distance en dimension 2
             entre les deux points est inférieure ou égale à la distance donnée.
        Pre-conditions:
        - point_1 et point_2 sont des coordonnées de points
        - distance est un réel positif.
        Post-conditions : ...
    """

    dx, dy = point_2[0] - point_1[0], point_2[1] - point_1[1]
    return dx*dx + dy*dy <= distance * distance


# x-----------x
# |  Buckets  |
# x-----------x

def iter_near(graph_shortcut, limits, bucket_id, point_id):

    # Initialisations
    points, buckets, distance = graph_shortcut

    bucket = buckets[bucket_id]
    point = points[point_id]

    # -- Limite --

    # Reculer
    bucket_in_id = limits[bucket_id] - 1
    while 0 <= bucket_in_id < len(bucket) and points[bucket[bucket_in_id]][0] >= point[0] - distance:

        if is_at_distance(point, points[bucket[bucket_in_id]], distance):
            yield bucket[bucket_in_id]
        
        bucket_in_id -= 1

    bucket_in_id, limits[bucket_id] = limits[bucket_id], bucket_in_id + 1

    # Avancer
    while bucket_in_id < len(bucket) and points[bucket[bucket_in_id]][0] < point[0] - distance:
        bucket_in_id += 1

    limits[bucket_id] = bucket_in_id

    # -- Suivants --

    while bucket_in_id < len(bucket) and points[bucket[bucket_in_id]][0] <= point[0] + distance:
        
        if bucket[bucket_in_id] != point_id and is_at_distance(point, points[bucket[bucket_in_id]], distance):
            yield bucket[bucket_in_id]
    
        bucket_in_id += 1


def analyse_bucket(bucket_id, graph_shortcut, clustering_shortcut):

    # Shortcut development
    points, buckets, distance = graph_shortcut
    register, groups, fusions = clustering_shortcut
    
    limits = defaultdict(int)
    for point_id in filter(lambda point_id: point_id not in register.keys(), buckets[bucket_id]):

        # Initialisations
        groups[point_id] = set([point_id])
        register[point_id] = point_id

        # Itérations
        for shift in range(0, 2):
            for aside_id in iter_near(graph_shortcut, limits, bucket_id - shift, point_id):

                if aside_id in register:

                    fusions[point_id].add(aside_id)

                else:

                    groups[point_id].add(aside_id)
                    register[aside_id] = point_id

                    # Sub analyse
                    for dbl_shift in range(-2 * shift, 2):
                        fusions[point_id].update(iter_near(graph_shortcut, limits, bucket_id + dbl_shift, aside_id))


# x--------x
# |  Main  |
# x--------x

def print_components_sizes(distance, points):
    """
    affichage des tailles triees de chaque composante
    """

    # x------------------x
    # |  Initialization  |
    # x------------------x

    points.sort()

    # Constantes
    BUCKET_SIZE = distance

    # Buckets
    buckets = defaultdict(list)

    for bucket_id, subgroup in groupby(enumerate(points), lambda point_ref: int(point_ref[1][1] // BUCKET_SIZE)):
        buckets[bucket_id].extend([i for i, _ in subgroup])

    buckets_keys = list(buckets.keys())
    buckets_keys.sort()

    # Clustering
    register, groups, fusions = ({}, {}, defaultdict(set))
            

    # x-------------x
    # |  Processes  |
    # x-------------x

    graph_multiprocessing(buckets_keys, analyse_bucket, (points, buckets, distance), (register, groups, fusions))


    # x-----------x
    # |  Fusions  |
    # x-----------x

    for i, near_groups in fusions.items():

        # Mise à jour du registre
        for id in near_groups:
            group_id = register[id]

            register_id = register[group_id]

            if register_id != register[i]:
                groups[register[i]].update(groups[register_id])

                for point_id in groups[register_id]:
                    register[point_id] = register[i]

                groups.pop(register_id)


    # Calcul du résultat
    counts = list((len(group) for group in groups.values()))
    counts.sort(reverse=True)

    print(counts, end='\n')


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
