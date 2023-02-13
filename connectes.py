#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from math import floor
from sys import argv
from itertools import product
from collections import defaultdict


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

def iter_bucket(points, bucket, current_index, x_limit, strict = False):
    """
        Def: Permet d'itérer sur un bucket jusqu'à la condition limite en x.
        Pre-conditions:
        - bucket est une liste de la forme [[*coordoonées], indice de la liste de coordoonées],
        - x_limit est un réel,
        - strict est un booléen.
        Post-conditions : ...

        WARNING: La modification de la taille de la liste de coordoonées n'est pas
                 prise en charge par la fonction.
        WARNING: Le point à l'index courant est toujours itéré.
    """

    bucket_id = bucket[1]

    while bucket_id < len(bucket[0]) and \
        ((    strict and points[bucket[0][bucket_id]][0] <  x_limit) or \
         (not strict and points[bucket[0][bucket_id]][0] <= x_limit) or \
         current_index == bucket[0][bucket_id]):

        yield bucket[0][bucket_id]
        bucket_id += 1


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

    # Buckets

    # Un "bucket" est une liste des points sur un découpage de l'axe Y.
    # L'intersection entre "buckets" et vide.

    BUCKET_SIZE = distance / 2

    last_observed_id = 0
    buckets = {
        'groups'  : defaultdict(lambda: [[], 0]),
        'isolates': defaultdict(lambda: [[], 0])
    }

    # Groups

    # Le registre est la liste des correspondances (point, point référent).
    # groups est l'état partiel courant des groupes et results en est l'état final.

    register, groups, results = {}, {}, {}

    # Buffers
    near_groups = set() # Groupes pouvant être fusionné avec le point courant.
    removing_buffer = set() # Points pouvant être supprimé des points isolés.

    # Listes des points pouvant lier deux groupes grâces à des points isolés.
    # La clé étant le test "ordonné du point du groupe est inférieure à l'ordonné
    # du point courant".
    # (aside_y < current_y)
    isolates_links = {
        True : { 'in': set(), 'out': set() },
        False: { 'in': set(), 'out': set() }
    }

    points.sort()


    # x-------------x
    # |  Main loop  |
    # x-------------x

    for i, point in enumerate(points):

        if i not in register:

            # x------------------x
            # |  Initialization  |
            # x------------------x


            # Components
            x, y = point
            bucket_id = floor(y / BUCKET_SIZE)

            # Clear buffers
            near_groups.clear()
            near_groups.add(i)

            for side in isolates_links.values():
                for category in side.values():
                    category.clear()

            # Groups
            groups[i] = set([i])
            register[i] = i


            # x----------x
            # |  Groups  |
            # x----------x

            # Observation des buckets à une distance de plus ou moins 4 du bucket courant
            for aside_bucket_id in range(max(bucket_id - 4, 0), bucket_id + 4 + 1):
                bucket = buckets['groups'][aside_bucket_id]

                # Suppression des points ne pouvant pas passer les tests
                # (n'apportant aucune information)
                for aside_id in iter_bucket(points, bucket, i, x - distance, True):
                    groups[register[aside_id]].remove(aside_id)

                    bucket[1] += 1

                # Efficient
                for aside_id in iter_bucket(points, bucket, i, x + distance):

                    if register[aside_id] not in near_groups:

                        point_y = points[aside_id][1]

                        if is_at_distance(point, points[aside_id], distance):
                            # In distance circle

                            near_groups.add(register[aside_id])

                            if aside_id in isolates_links[point_y < y]['out']:
                                isolates_links[point_y < y]['out'].remove(aside_id)

                        elif is_at_distance(points[aside_id], (x, y + ((point_y >= y) * 2 - 1) * distance), distance):
                            # In double distance circle

                            isolates_links[point_y < y]['out'].add(aside_id)


            # x------------x
            # |  Isolates  |
            # x------------x

            # News
            while last_observed_id < len(points) and points[last_observed_id][0] <= x + distance:
                buckets['isolates'][floor(points[last_observed_id][1] // BUCKET_SIZE)][0].append(last_observed_id)

                last_observed_id += 1

            # Observed

            # Observation des buckets à une distance de plus ou moins 2 du bucket courant
            for aside_bucket_id in range(max(bucket_id - 2, 0), bucket_id + 2 + 1):
                bucket = buckets['isolates'][aside_bucket_id]

                # Suppression des points ne pouvant pas passer les tests (n'apportant aucune information)
                for _ in iter_bucket(points, bucket, i, x, True):
                    bucket[1] += 1

                # Efficient
                removing_buffer.clear()

                for aside_id in iter_bucket(points, bucket, i, x + distance):
                    point_y = points[aside_id][1]

                    if is_at_distance(point, points[aside_id], distance):
                        # In distance circle

                        groups[i].add(aside_id)
                        register[aside_id] = i

                        if is_at_distance(points[aside_id], (x, y + ((point_y > y) * 2 - 1) * distance), distance):
                            isolates_links[point_y < y]['in'].add(aside_id)

                        buckets['groups'][floor(point_y // BUCKET_SIZE)][0].append(aside_id)
                        removing_buffer.add(aside_id)

                for aside_id in removing_buffer:
                    bucket[0].remove(aside_id)


            # x--------------------x
            # |  Isolates's links  |
            # x--------------------x

            # Boucle sur les possibilités observés jusqu'à en trouver au maximum
            # une inférieure et une supérieure.

            for in_points in isolates_links.values():

                for k, j in product(in_points['in'], in_points['out']):

                    if is_at_distance(points[j], points[k], distance):
                        # In distance circle

                        near_groups.add(register[j])
                        break


            # x-----------x
            # |  Fusions  |
            # x-----------x

            # Recherche du plus grand groupe
            max_group_id, max_count = i, len(groups[i])

            for group_id in near_groups:
                if len(groups[group_id]) > max_count:
                    max_group_id, max_count = group_id, len(groups[group_id])

            near_groups.remove(max_group_id)

            # Ajout d'un résultat
            results[i] = set()
            results[i].update(groups[i])

            # Mise à jour du registre
            for group_id in near_groups:
                groups[max_group_id].update(groups[group_id])
                results[max_group_id].update(results[group_id])

                results.pop(group_id)

                for point_id in groups[group_id]:
                    register[point_id] = max_group_id

                register[group_id] = max_group_id


    # Calcul du résultat
    counts = list((len(group) for group in results.values()))
    counts.sort(reverse=True)

    print(counts)


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()
