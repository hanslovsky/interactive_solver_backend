import logging
import logging.config
import nifty
import numpy as np
import os
import signal
import solver_backend
import sys
import time
import yaml

if __name__ == "__main__":
    import argparse

    default_level = 'INFO'

    parser = argparse.ArgumentParser()
    parser.add_argument('--graph'                     , '-g', default='/data/hanslovskyp/constantin-example-data/data/mc-graph.npy')
    parser.add_argument('--costs'                     , '-c', default='/data/hanslovskyp/constantin-example-data/data/mc-costs.npy')
    parser.add_argument('--address'                   , '-a', default='ipc:///tmp/mc-solver')
    parser.add_argument('--solution-publisher-address', '-s', default='ipc:///tmp/current-solution')
    parser.add_argument('--logging-config'            , '-l', default='/home/hanslovskyp/workspace/bigcat-future/interactive_solver_backend/logger.yaml')

    args    = parser.parse_args()
    costs   = np.load(args.costs, allow_pickle=False)
    address = args.address
    graph   = nifty.graph.UndirectedGraph()

    graph.deserialize(np.load(args.graph, allow_pickle=False))

    try:
        with open(args.logging_config, 'r') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    except:
        try:
            logging.basicConfig(level=args.logging_config)
        except:
            logging.basicConfig(level=default_level)


    def initial_solution(graph, costs):
        solution = solver_backend.solve_multicut(graph, costs)
        print(" Got solution!")
        return solution
    server = solver_backend.SolverServer(graph, costs, address, args.solution_publisher_address, initial_solution)
    server.start()

    def handle_signal_interrupt(signal, frame):
        print("Stopping server!")
        server.stop()
    signal.signal(signal.SIGINT, handle_signal_interrupt)

