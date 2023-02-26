#!/usr/bin/env python3

from multiprocessing import Process, Manager, cpu_count


def graph_multiprocessing(keys, analyse_function, static_args, dynamic_args):
    count    = max(min(len(keys) // 2, cpu_count() - 1), 0)

    effectif = len(keys) // count
    rest     = len(keys) %  count

    manager = Manager()
    processes = []

    returns = manager.dict()

    # Start
    for process_id in range(0, count):
        current = (process_id + 1) * effectif + min(rest, (process_id + 1))
        subkeys = keys[current + 1:current + effectif + int(process_id + 1 < rest)]

        process = Process(target=process_main, args=(
            process_id, 
            subkeys, 
            returns, 
            analyse_function, 
            static_args, 
            dynamic_args
        ))
        process.start()

        processes.append(process)
    
    process_loop(keys[0:effectif + min(rest, 1)], analyse_function, static_args, dynamic_args)

    # Join
    for process_id, process in enumerate(processes):
        process.join()

        for obj, process_obj in zip(dynamic_args, returns[process_id]):
            obj.update(process_obj)

    # Limits
    for process_id in range(0, count):
        bucket_id = (process_id + 1) * effectif + min(rest, (process_id + 1))

        analyse_function(bucket_id, static_args, dynamic_args)


def process_loop(subkeys, analyse_function, static_args, dynamic_args):
    for bucket_id in subkeys:
        analyse_function(bucket_id, static_args, dynamic_args)

def process_main(process_id, subkeys, returns, analyse_function, static_args, dynamic_args):

    dynamic_copies = []
    for obj in dynamic_args:
        dynamic_copies.append(obj.copy())

    process_loop(subkeys, analyse_function, static_args, dynamic_copies)

    returns[process_id] = dynamic_copies
