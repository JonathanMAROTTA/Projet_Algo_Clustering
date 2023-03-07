#!/usr/bin/env python3

from multiprocessing import Process, Manager, Pipe, cpu_count, Lock
from time import perf_counter
from collections import defaultdict

def graph_multiprocessing(keys, analyse_function, graph):
    count    = max(min(len(keys) // 3, cpu_count()), 1)

    effectif = len(keys) // count
    rest     = len(keys) %  count

    print('')
    print('  Nombre de processus total :', count)
    print('  Bucket / processus :', effectif)
    print('  Reste :', rest)
    print('')

    # -- Initialize --
    manager = Manager()

    register = manager.dict()
    returns = manager.dict()
    
    # Locks
    first_locks = Lock(), Lock()
    lock_last = first_locks[1]

    # -- Run process --
    processes = []

    for process_id in range(1, count):
        current = process_id * effectif + min(rest, process_id)
        subkeys = keys[current:current + effectif + int(process_id < rest)]

        lock_first, lock_last = lock_last, Lock()

        process = Process(target=process_main, args=(
            process_id, 
            subkeys,
            returns,
            (lock_first, lock_last),
            analyse_function,
            register,
            graph
        ))
        process.start()

        processes.append(process)

    process_main(
        0, 
        keys[0:effectif + min(rest, 1)], 
        returns, 
        first_locks,
        analyse_function, 
        register,
        graph
    )

    # -- Join process --
    for process_id, process in enumerate(processes):
        process.join()

    # -- Return --
    fusions = defaultdict(set)

    for local_fusions in returns.values():
        fusions.update(local_fusions)

    return register, fusions


def process_main(process_id, subkeys, returns, locks, analyse_function, register, graph):

    # -- Initialise --
    lock_first, lock_last = locks

    local_fusions = defaultdict(set)

    # -- Run --
    with lock_first:
        analyse_function(subkeys[0], register, graph, local_fusions)

    for bucket_id in subkeys[1:-1]:
        analyse_function(bucket_id, register, graph, local_fusions)

    with lock_last:
        analyse_function(subkeys[-1], register, graph, local_fusions)

    # -- Return --
    returns[process_id] = local_fusions
