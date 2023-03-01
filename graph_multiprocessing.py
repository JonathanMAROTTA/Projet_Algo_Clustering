#!/usr/bin/env python3

from multiprocessing import Process, Manager, Pipe, cpu_count


def graph_multiprocessing(keys, analyse_function, static_args, dynamic_args):
    count    = max(min(len(keys) // 4, cpu_count()), 1)

    effectif = len(keys) // count
    rest     = len(keys) %  count

    print('')
    print('  Nombre de processus total :', count)
    print('  Bucket / processus :', effectif)
    print('  Reste :', rest)
    print('')

    manager = Manager()
    processes = []

    returns = manager.dict()

    # -- Start --
    main_pipe_send, pipe_recv = Pipe()

    for process_id in range(1, count):
        current = process_id * effectif + min(rest, process_id)
        subkeys = keys[current:current + effectif + int(process_id < rest)]

        pipe_send, pipe_next_recv = Pipe()

        process = Process(target=process_main, args=(
            process_id, 
            subkeys,
            returns,
            (pipe_send, pipe_recv),
            analyse_function,
            static_args, 
            dynamic_args
        ))
        process.start()

        processes.append(process)


        pipe_recv = pipe_next_recv

    process_main(
        0, 
        keys[0:effectif + min(rest, 1)], 
        returns, 
        (main_pipe_send, None), 
        analyse_function, 
        static_args, 
        dynamic_args
    )

    # -- Join --

    for process_id, process in enumerate(processes):
        process.join()

    # Fusion
    for dynamic_copy in returns.values():
        for obj, return_obj in zip(dynamic_args, dynamic_copy):
            obj.update(return_obj)


def process_loop(pipes, subkeys, analyse_function, static_args, dynamic_args):
    analyse_function(subkeys[-1], static_args, dynamic_args)
    analyse_function(subkeys[-2], static_args, dynamic_args)
    pipes[0].send(dynamic_args)

    for bucket_id in subkeys[2:-2]:
        analyse_function(bucket_id, static_args, dynamic_args)

    if pipes[1] is not None:
        dynamic_recv = pipes[1].recv()

        for obj, recv_obj in zip(dynamic_args, dynamic_recv):
            obj.update(recv_obj)
    
    analyse_function(subkeys[0], static_args, dynamic_args)
    analyse_function(subkeys[1], static_args, dynamic_args)
        


def process_main(process_id, subkeys, returns, pipes, analyse_function, static_args, dynamic_args):

    dynamic_copies = [obj.copy() for obj in dynamic_args]

    process_loop(pipes, subkeys, analyse_function, static_args, dynamic_copies)

    returns[process_id] = dynamic_copies
