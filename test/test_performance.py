import unittest

from simulation.model import CommunicationNetwork, TimeVaryingHypergraph, EntityNotFound
from simulation.minimal_paths import single_source_dijkstra_vertices, single_source_dijkstra_hyperedges, DistanceType

import timeit
from datetime import timedelta


class TestMinimalpathPerformance(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initalization
        self.time_graph = TimeVaryingHypergraph(hedges = {
            'e1': ['v1', 'v2','v3', 'v4','v5', 'v6'],
            'e2': ['v2', 'v3','v5', 'v6'],
            'e3': ['v1', 'v4','v6', 'v2', 'v3'],
            'e4': ['v2', 'v3']
        }, timings = {
            'e1': timedelta(days=1),
            'e2': timedelta(days=2),
            'e3': timedelta(days=3),
            'e4': timedelta(days=4)
        })
        self.time_source_vertex = 'v1'
        self.time_distance_type = DistanceType.FASTEST

    def test_minimalpath_performance(self):
                # Measure the execution time for function single_source_dijkstra_hyperedges
        hyperedges_time = timeit.timeit(
            stmt="single_source_dijkstra_hyperedges(self.time_graph, self.time_source_vertex, self.time_distance_type)",
            setup="from simulation.minimal_paths import single_source_dijkstra_hyperedges, TimeVaryingHypergraph, DistanceType",
            number=2000,
            globals=vars())

        # Measure the execution time for function single_source_dijkstra_vertices
        vertices_time = timeit.timeit(
            stmt="single_source_dijkstra_vertices(self.time_graph, self.time_source_vertex, self.time_distance_type)",
            setup="from simulation.minimal_paths import single_source_dijkstra_vertices, TimeVaryingHypergraph, DistanceType",
            number=2000,
            globals=vars())

        # Compare the execution times

        print('\n-------------------- Performance report --------------------')
        print(f'Single source dijkstras using hyperedges : {hyperedges_time:.6f} seconds')
        print(f'Single source dijkstras using vertices   : {vertices_time:.6f}   seconds')
        print('\n\033[96mResults: \033[0m')
        winner = "Dijkstras using hyperedges" if min(hyperedges_time, vertices_time) == hyperedges_time else "Dijkstras using vertices"
        print(f'In this run \033[92m {winner} \033[0m was the fastest by {abs(min(hyperedges_time, vertices_time) - max(hyperedges_time, vertices_time)):.6f} seconds')
        print('------------------------------------------------------------\n')
        self.assertLess(hyperedges_time, vertices_time) if min(hyperedges_time, vertices_time) == hyperedges_time else self.assertLess(vertices_time, hyperedges_time)
