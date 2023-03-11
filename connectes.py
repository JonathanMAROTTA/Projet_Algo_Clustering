#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from sys import argv
from itertools import groupby
from collections import defaultdict

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
        Définition: Retourne le booléen indiquant si
        la distance en dimension 2 entre les deux 
        points est inférieure ou égale à la distance donnée.

        Paramètres:
        - point_1, point_2 : les deux coordonées de points
        - distance : réel positif représentant une distance

        Pré-conditions  : ...
        Post-conditions : ...
    """

    dx, dy = point_2[0] - point_1[0], point_2[1] - point_1[1]
    return dx*dx + dy*dy <= distance * distance


# x--------x
# |  cuts  |
# x--------x

def iter_near(graph, limits, cuts_key, point_id, forward = None):
    """
        Itérateur efficace sur les points à une distance
        maximale d'un point et d'un cut donnée.
        
        Paramètres:
        - graph : raccourci des structures données (points, cuts, distance)
        - limits : dictionnaire d'entier (valeur par défaut 0) ayant pour clef
                   un indice du dictionnaire de cut et pour valeur un indice
                   de cut.
        - cuts_key : clef du dictionnaire (cut à cibler)
        - point_id : indice de point centre, indice non-itéré
        - forward : booléen
            * True  : itérer sur les points d'abscisses supérieures au point d'indice point_id
            * False : itérer sur les points d'abscisses inférieures au point d'indice point_id
            * None  : itérer sur tous les points

        Pré-conditions  :
        - l'indice point_id est supérieur à l'indice point_id de l'appel précédant 
          (pour un même indice du dictionnaire de cut)
        - les cuts sont triés 
        - les valeurs de limits sont telle que tous indices du cut (de clef de dictionnaire
          de cuts) inférieurs à la valeur ne peuvent être à bonne distance
          
        Post-conditions :
        - les valeurs de limits sont telle que tous indices du cut (de clef de dictionnaire
          de cuts) inférieurs à la valeur ne peuvent être à bonne distance
    """

    # Initialisations
    points, cuts, distance = graph

    cut = cuts[cuts_key]
    point = points[point_id]

    # -- Before limit --

    cut_id = limits[cuts_key]

    while cut_id < len(cut) and points[cut[cut_id]][0] < point[0] - distance:
        cut_id += 1

    limits[cuts_key] = cut_id

    # -- After limit --

    if not forward or forward is None:
        # Before
        while cut_id < len(cut) and cut[cut_id] < point_id:
        
            if is_at_distance(point, points[cut[cut_id]], distance):
                yield cut[cut_id]

            cut_id += 1
    else:
        # Skit before
        while cut_id < len(cut) and cut[cut_id] < point_id:
            cut_id += 1

    # Skip current
    cut_id += cut_id < len(cut) and int(cut[cut_id] == point_id)

    # After
    if forward or forward is None:
        while cut_id < len(cut) and points[cut[cut_id]][0] <= point[0] + distance:
            
            if is_at_distance(point, points[cut[cut_id]], distance):
                yield cut[cut_id]

            cut_id += 1

def iter_shift(graph, cuts_limits, cuts_key, relative_interval, point_id, forward = None):
    """
        Itérateur efficace sur les points à une distance
        maximale d'un point et d'un interval de cuts donné.
        
        Paramètres:
        - graph : raccourci des structures données (points, cuts, distance)
        - limits : dictionnaire d'entier (valeur par défaut 0) ayant pour clef
                   un indice du dictionnaire de cut et pour valeur un indice
                   de cut.
        - relative_interval : interval de clefs du dictionnaire (cuts à cibler)
        - point_id : indice de point centre, indice non-itéré
        - forward : booléen
            * True  : itérer sur les points d'abscisses supérieures au point d'indice point_id
            * False : itérer sur les points d'abscisses inférieures au point d'indice point_id
            * None  : itérer sur tous les points

        Pré-conditions  :
        - l'indice point_id est supérieur à l'indice point_id de l'appel précédant 
          (pour un même indice du dictionnaire de cut)
        - les cuts sont triés 
        - les valeurs de limits sont telle que tous indices du cut (de clef de dictionnaire
          de cuts) inférieurs à la valeur ne peuvent être à bonne distance
          
        Post-conditions :
        - les valeurs de limits sont telle que tous indices du cut (de clef de dictionnaire
          de cuts) inférieurs à la valeur ne peuvent être à bonne distance
    """

    for aside_cut_id in range(max(cuts_key + relative_interval[0], 0), cuts_key + relative_interval[1] + 1):
        yield from iter_near(graph, cuts_limits, aside_cut_id, point_id, forward)


# x------------x
# |  referents  |
# x------------x

def not_already_merged(referents, cluster_to_merge, referent_id, point_id):
    """
        Prédicat indiquant si deux points ont été fusionnés.
        
        Paramètres:
        - referents : dictionnaire des référents
        - cluster_to_merge : cluster à fusionner
        - referent_id : point 1 (référent)
        - point_id : point 2

        Pré-conditions  : ...
        Post-conditions : ...
    """

    return point_id not in referents or (
        referents[point_id] != referent_id and
        ( referents[point_id] not in cluster_to_merge or referent_id         not in cluster_to_merge[referents[point_id]] ) and
        ( referent_id         not in cluster_to_merge or referents[point_id] not in cluster_to_merge[referent_id        ] )
    )

def referents_add(referents, cluster_to_merge, wait_to_merge, referent_id, point_id):
    """
        Ajoute un référent à un point.
        
        Paramètres:
        - referents : dictionnaire des référents
        - cluster_to_merge : cluster à fusionner
        - wait_to_merge : liste des points en attente de fusion
        - referent_id : point 1 (référent)
        - point_id : point 2

        Pré-conditions  :
        - point_id ne possède pas de référent
        Post-conditions : ...
    """

    # Ajout du référent dans le dictionnaire de référents
    referents[point_id] = referent_id

    # Ajout d'une fusion pour chaque fusion en attente pour le point point_id
    for old_ref_id in filter(
            lambda old_ref_id : not_already_merged(referents, cluster_to_merge, referent_id, old_ref_id), 
            wait_to_merge[point_id]
        ):
        cluster_to_merge[old_ref_id].add(referent_id)

    wait_to_merge[point_id].clear()

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

    # Cuts
    cuts = defaultdict(list)

    for cut_key, cut_content in groupby(range(len(points)), lambda point_id: int(points[point_id][1] // distance)):
        cuts[cut_key].extend(cut_content)

    # Limits
    cuts_limits, cuts_limits_others = defaultdict(int), defaultdict(int)

    # Shortcut
    graph = (points, cuts, distance)

    # Clustering
    referents = {}

    cluster_to_merge = defaultdict(set)
    wait_to_merge    = defaultdict(set)
            

    # x--------x
    # |  Loop  |
    # x--------x

    # Itération sur les points n'ayant pas de référents
    for referent_id in filter(lambda point_id: point_id not in referents, range(len(points))):

        point = points[referent_id]

        # x------------------x
        # |  Initialization  |
        # x------------------x

        # Components
        y = point[1]
        cut_id = int(y // distance)

        # Le référent du point proche devient lui-même
        referents_add(referents, cluster_to_merge, wait_to_merge, referent_id, referent_id)


        # x----------x
        # |  Groups  |
        # x----------x

        # Itération sur les points :
        # - de référent différent du point courant
        # - non fusionné avec le cluster courant
        # - d'abscisse inférieure au point courant
        # - de bonne distance au point courant

        for near_id in filter(
                lambda near_id: not_already_merged(referents, cluster_to_merge, referent_id, near_id), 
                iter_shift(graph, cuts_limits, cut_id, (-1, 1), referent_id, False)
            ):
            cluster_to_merge[referent_id].add(referents[near_id])

        # Itération sur les points :
        # - d'abscisse supérieure au point courant
        # - de bonne distance au point courant

        for near_id in iter_shift(graph, cuts_limits, cut_id, (-1, 1), referent_id, True):

            if near_id not in referents.keys():

                # Le référent du point proche devient le point courant
                referents_add(referents, cluster_to_merge, wait_to_merge, referent_id, near_id)

                # Itération sur les points :
                # - de bonne distance du point proche
                # - non à bonne distance du point courant
                # - non déjà fusionné avec le point courant

                for far_id in filter(
                        lambda far_id: not_already_merged(referents, cluster_to_merge, referent_id, far_id) and
                            not is_at_distance(point, points[far_id], distance),
                        iter_shift(graph, cuts_limits_others, cut_id, (-1, +1), near_id)
                    ):

                    if far_id in referents.keys():

                        # Ajout d'une fusion
                        cluster_to_merge[referent_id].add(referents[far_id])
                    else:

                        # Ajout d'une fusion future
                        wait_to_merge[far_id].add(referent_id)
                    
            elif not_already_merged(referents, cluster_to_merge, referent_id, near_id):

                # Ajout d'une fusion
                cluster_to_merge[referent_id].add(referents[near_id])


    # x-----------x
    # |  cluster_to_merge  |
    # x-----------x

    # Calcul du résultat
    counts = fusion(referents, cluster_to_merge)

    print(sorted(counts, reverse=True))

    return sorted(counts, reverse=True) # To check validity


def init_counts(referents):
    """
    Create a dict of :\n
    key = centroid\n
    value = number of points in group[key]
    """
    counts = defaultdict(int)

    for _, point_id in referents.items():
        counts[point_id] += 1

    return counts
    

def fusion(referents, cluster_to_merge):
    """Réalise la fusion des points dans des groupes définitifs"""

    counts = init_counts(referents)

    # c1 ----> c2 ----> c3 ----> c1
    # c1       c2       c3       c1

    # c1 -> c2 ; c3 -> c2
    # c1    c2 ; c3    c2
    # c1    c1 ; c3    c1
    # c1    c1 ; c1    c1

    # On peut voir fusion comme la gestion de différents arbres.

    # cluster_to_merge   ; key   : referent_id
    #           ; value : set(referent_id)

    # cluster_to_merge   ; key   : node_id
    #           ; value : set(node_id)

    for node, nodes_to_merge in cluster_to_merge.items():

        # Recherche de la racine
        root = referents[node]
        while root != referents[root]:
            root = referents[root]

        referents[node] = root


        for node_to_merge in nodes_to_merge:

            # Recherche de la racine
            root_to_merge = referents[node_to_merge]
            while root_to_merge != referents[root_to_merge]:
                root_to_merge = referents[root_to_merge]

            referents[node_to_merge] = root_to_merge


            if root != root_to_merge:

                # Ajout du compte de points dans l'arbre d'identifiant root_to_merge
                counts[root] += counts[root_to_merge]

                # Suppression de l'arbre d'identifiant root_to_merge
                referents[root_to_merge] = root
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
