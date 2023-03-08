#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from math import floor
from sys import argv
from itertools import product, groupby
from collections import defaultdict

from connectes_tests import Perf, test_rapport


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
    print(len(points))
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

    with Perf("Global", True):
        # x------------------x
        # |  Initialization  |
        # x------------------x

        with Perf("Global init"):
            points.sort()

            # Buckets

            # Un "bucket" est une liste des points sur un découpage de l'axe Y.
            # L'intersection entre "buckets" et vide.
            
            buckets = defaultdict(list)
            buckets_limits, buckets_limits_others = defaultdict(int), defaultdict(int)

            graph = (points, buckets, distance)

            # A voir
            for bucket_id, bucket_content in groupby(range(len(points)), lambda point_id: int(points[point_id][1] // distance)):
                buckets[bucket_id].extend(bucket_content)

            # Groups

            # Le registre est la liste des correspondances (point, point référent).
            # groups est l'état partiel courant des groupes et results en est l'état final.

            register, fusions = {}, defaultdict(set)

        # Tests
        segments = { 'groups': [], 'fusions': [] }

        # x-------------x
        # |  Main loop  |
        # x-------------x

        for referent_id in filter(lambda point_id: point_id not in register, range(len(points))):

            point = points[referent_id]

            with Perf("Loop init"):
                # x------------------x
                # |  Initialization  |
                # x------------------x

                # Components
                x, y = point
                bucket_id = int(y // distance)

                # Groups
                register[referent_id] = referent_id


            # x----------x
            # |  Groups  |
            # x----------x

            with Perf("Groups"):
                # Observation des buckets à une distance de plus ou moins 4 du bucket courant
                for near_id in iter_shift(graph, buckets_limits, bucket_id, (-1, 0), referent_id):

                    if near_id not in register.keys():

                        register[near_id] = referent_id
                        segments['groups'].append((points[referent_id], points[near_id]))

                        fusions[referent_id].update(filter(
                            lambda far_id: 
                                far_id not in register or (
                                    register[far_id] != referent_id and
                                    ( register[far_id] not in fusions or referent_id        not in fusions[register[far_id]] ) and
                                    ( referent_id        not in fusions or register[far_id] not in fusions[referent_id       ] )
                                ) and
                                not is_at_distance(point, points[far_id], distance),
                            iter_shift(graph, buckets_limits_others, bucket_id, (-1, +1), near_id)
                        ))

                    else:

                        fusions[referent_id].add(register[near_id])


        print(f"\n  Fin de la boucle principale : {Perf.times['Groups'][0]:7.4f}s\n")


        # x-----------x
        # |  Fusions  |
        # x-----------x

        # Tests
        for point_id, nears in fusions.items():
            for aside_id in nears:
                segments['fusions'].append((points[point_id], points[aside_id]))
        # -----

        groups = defaultdict(set)
        for aside_id, point_id in register.items():
            groups[point_id].add(aside_id) 


        with Perf("Fusions"):
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

    test_rapport(points, buckets, distance, groups, segments)

    print(counts)


# For tests perfs
def main_perfs(filenames):
    for instance in filenames:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
