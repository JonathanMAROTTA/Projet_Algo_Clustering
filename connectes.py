#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from sys import argv
from itertools import product, groupby
from collections import defaultdict, Counter

from libtests import Perf, test_rapport


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

def iter_near(graph, limits, bucket_id, point_id, forward = None):

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

    while bucket_in_id < len(bucket) and bucket[bucket_in_id] < point_id:
        
        if (not forward or forward is None) and is_at_distance(point, points[bucket[bucket_in_id]], distance):
            yield bucket[bucket_in_id]

        bucket_in_id += 1

    bucket_in_id += bucket_in_id < len(bucket) and int(bucket[bucket_in_id] == point_id)

    if forward or forward is None:
        while bucket_in_id < len(bucket) and points[bucket[bucket_in_id]][0] <= point[0] + distance:
            
            if is_at_distance(point, points[bucket[bucket_in_id]], distance):
                yield bucket[bucket_in_id]

            bucket_in_id += 1

def iter_shift(graph, buckets_limits, bucket_id, relative_interval, point_id, forward = None):

    for aside_bucket_id in range(max(bucket_id + relative_interval[0], 0), bucket_id + relative_interval[1] + 1):
        yield from iter_near(graph, buckets_limits, aside_bucket_id, point_id, forward)


# x------------x
# |  Register  |
# x------------x

def register_add(register, referent_id, near_id, wait_to_add, fusions):
    register[near_id] = referent_id
    for old_ref_id in filter(
            lambda old_ref_id : referent_id != old_ref_id and ( referent_id not in fusions or old_ref_id not in fusions[referent_id] ), 
            wait_to_add[near_id]
        ):
        fusions[old_ref_id].add(referent_id)

    wait_to_add[near_id].clear()

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
    wait_to_add = defaultdict(set)

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

    for referent_id in filter(lambda point_id: point_id not in register, range(len(points))):

        point = points[referent_id]

        # x------------------x
        # |  Initialization  |
        # x------------------x

        # Components
        x, y = point
        bucket_id = int(y // distance)

        # Groups
        register_add(register, referent_id, referent_id, wait_to_add, fusions)


        # x----------x
        # |  Groups  |
        # x----------x

        # Observation des buckets à une distance de plus ou moins 2 du bucket courant
        for near_id in filter(
                lambda near_id: register[near_id] != referent_id and referent_id not in fusions[register[near_id]], 
                iter_shift(graph, buckets_limits, bucket_id, (-1, 1), referent_id, False)
            ):
            fusions[referent_id].add(register[near_id])

        for near_id in iter_shift(graph, buckets_limits, bucket_id, (-1, 1), referent_id, True):

            if near_id not in register.keys():

                register_add(register, referent_id, near_id, wait_to_add, fusions)

                for far_id in filter(
                        lambda far_id: 
                            far_id not in register or (
                                register[far_id] != referent_id and
                                ( register[far_id] not in fusions or referent_id      not in fusions[register[far_id]] ) and
                                ( referent_id      not in fusions or register[far_id] not in fusions[referent_id     ] )
                            ) and
                            not is_at_distance(point, points[far_id], distance),
                        iter_shift(graph, buckets_limits_others, bucket_id, (-1, +1), near_id)
                    ):

                    if far_id in register.keys():
                        fusions[referent_id].add(register[far_id])
                    else:
                        wait_to_add[far_id].add(referent_id)
                    
            elif register[near_id] != referent_id and referent_id not in fusions[register[near_id]]:
                fusions[referent_id].add(register[near_id])


    # x-----------x
    # |  Fusions  |
    # x-----------x

    # Calcul du résultat
    counts = fusion(register, fusions)

    print(sorted(counts, reverse=True))

    return sorted(counts, reverse=True) # To check validity


def init_counts(register):
    """
    Create a dict of :\n
    key = centroid\n
    value = number of points in group[key]
    """
    counts = defaultdict(int)

    for _, point_id in register.items():
        counts[point_id] += 1

    return counts
    

def fusion(register, fusions):
    """Réalise la fusion des points dans des groupes définitifs"""

    counts = init_counts(register)

    # c1 ----> c2 ----> c3 ----> c1
    # c1       c2       c3       c1

    # c1 -> c2 ; c3 -> c2
    # c1    c2 ; c3    c2
    # c1    c1 ; c3    c1
    # c1    c1 ; c1    c1

    # On peut voir fusion comme la gestion de différents arbres.

    # fusions   ; key   : referent_id
    #           ; value : set(referent_id)

    # fusions   ; key   : node_id
    #           ; value : set(node_id)

    for node, nodes_to_merge in fusions.items():

        # Recherche de la racine
        root = register[node]
        while root != register[root]:
            root = register[root]

        register[node] = root


        for node_to_merge in nodes_to_merge:

            # Recherche de la racine
            root_to_merge = register[node_to_merge]
            while root_to_merge != register[root_to_merge]:
                root_to_merge = register[root_to_merge]

            register[node_to_merge] = root_to_merge


            if root != root_to_merge:

                # Ajout du compte de points dans l'arbre d'identifiant root_to_merge
                counts[root] += counts[root_to_merge]

                # Suppression de l'arbre d'identifiant root_to_merge
                register[root_to_merge] = root
                del counts[root_to_merge]

    return list(number_of_child for number_of_child in counts.values())


# For tests perfs
def main_perfs(distance, points):
    return print_components_sizes(distance, points)


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
