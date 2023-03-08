#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from math import floor
from sys import argv
from itertools import product, groupby
from collections import defaultdict

from lib_test import Perf, test_rapport


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

def iter_near(graph, limits, bucket_id, point_id):

    # Initialisations
    points, buckets, distance = graph

    bucket = buckets[bucket_id]
    point = points[point_id]

    # -- Before limit --

    bucket_in_id = limits[bucket_id]

    while bucket_in_id < len(bucket) and points[bucket[bucket_in_id]][0] < point[0] - distance:
        bucket_in_id += 1

    limits[bucket_id] = bucket_in_id

    # -- Suivants --

    while bucket_in_id < len(bucket) and points[bucket[bucket_in_id]][0] <= point[0] + distance:
        
        if bucket[bucket_in_id] != point_id and is_at_distance(point, points[bucket[bucket_in_id]], distance):
            yield bucket[bucket_in_id]

        bucket_in_id += 1


def iter_shift(graph, buckets_limits, bucket_id, relative_interval, point_id):

    for aside_bucket_id in range(max(bucket_id + relative_interval[0], 0), bucket_id + relative_interval[1] + 1):
        yield from iter_near(graph, buckets_limits, aside_bucket_id, point_id)


# x--------x
# |  Main  |
# x--------x

def print_components_sizes(distance, points):
    """
    affichage des tailles triees de chaque composante
    """

    with Perf(0):
        # x------------------x
        # |  Initialization  |
        # x------------------x

        with Perf(1):
            points.sort()

            # Buckets

            # Un "bucket" est une liste des points sur un découpage de l'axe Y.
            # L'intersection entre "buckets" et vide.

            BUCKET_SIZE = distance
            
            buckets, buckets_limits, buckets_limits_others = defaultdict(list), defaultdict(int), defaultdict(int)

            graph = (points, buckets, distance)

            # A voir
            for bucket_id, bucket_content in groupby(range(len(points)), lambda point_id: int(points[point_id][1] // BUCKET_SIZE)):
                buckets[bucket_id].extend(bucket_content)

            # Groups

            # Le registre est la liste des correspondances (point, point référent).
            # groups est l'état partiel courant des groupes et results en est l'état final.

            register, fusions = {}, defaultdict(set)

        # x-------------x
        # |  Main loop  |
        # x-------------x

        for point_id in filter(lambda point_id: point_id not in register, range(len(points))):

            point = points[point_id]

            with Perf(2):
                # x------------------x
                # |  Initialization  |
                # x------------------x

                # Components
                x, y = point
                bucket_id = int(y // BUCKET_SIZE)

                # Groups
                register[point_id] = point_id


            # x----------x
            # |  Groups  |
            # x----------x

            with Perf(3):
                # Observation des buckets à une distance de plus ou moins 4 du bucket courant
                for aside_id in iter_shift(graph, buckets_limits, bucket_id, (-1, 0), point_id):

                    if aside_id not in register.keys():

                        register[aside_id] = point_id

                        fusions[point_id].update(filter(
                            lambda other_id: 
                                other_id not in register or (
                                    register[other_id] != point_id and
                                    ( register[other_id] not in fusions or point_id           not in fusions[register[other_id]] ) and
                                    ( point_id           not in fusions or register[other_id] not in fusions[point_id          ] )
                                ) and
                                not is_at_distance(point, points[other_id], distance),
                            iter_shift(graph, buckets_limits_others, bucket_id, (-1, +1), aside_id)
                        ))

                    else:

                        fusions[point_id].add(register[aside_id])


        # x-----------x
        # |  Fusions  |
        # x-----------x

        groups = defaultdict(set)
        for aside_id, point_id in register.items():
            groups[point_id].add(aside_id) 


        with Perf(6):
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

    test_rapport(points, buckets, BUCKET_SIZE, groups)

    print(counts)



def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
