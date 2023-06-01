import unittest

from simulation.model import CommunicationNetwork, TimeVaryingHypergraph, EntityNotFound
from simulation.minimal_paths import single_source_dijkstra_vertices, single_source_dijkstra_hyperedges, DistanceType

from datetime import timedelta

class TestMinimalPath(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization
        self.cn = CommunicationNetwork({'h1': ['v1', 'v2'], 'h2': ['v2', 'v3'], 'h3': ['v3', 'v4']}, {'h1': 1, 'h2': 2, 'h3': 3})

    def test_1(self):
        self.assertEqual(single_source_dijkstra_vertices(
            self.cn, 'v1', DistanceType.SHORTEST, min_timing=0), {'v2': 1, 'v3': 2, 'v4': 3})

    def test_2(self):
        result_1 = single_source_dijkstra_vertices(
            self.cn, 'v1', DistanceType.SHORTEST, min_timing=0)
        result_2 = single_source_dijkstra_hyperedges(
            self.cn, 'v1', DistanceType.SHORTEST, min_timing=0)
        self.assertEqual(
            result_1, result_2, 'Single-source Dijkstra implementations are not equivalent')

    def test_3(self):
        result_1 = single_source_dijkstra_vertices(
            self.cn, 'v1', DistanceType.FASTEST, min_timing=0)
        result_2 = single_source_dijkstra_hyperedges(
            self.cn, 'v1', DistanceType.FASTEST, min_timing=0)
        self.assertEqual(
            result_1, result_2, 'Single-source Dijkstra implementations are not equivalent')

    def test_4(self):
        result_1 = single_source_dijkstra_vertices(
            self.cn, 'v1', DistanceType.FOREMOST, min_timing=0)
        result_2 = single_source_dijkstra_hyperedges(
            self.cn, 'v1', DistanceType.FOREMOST, min_timing=0)
        self.assertEqual(
            result_1, result_2, 'Single-source Dijkstra implementations are not equivalent')

class TestHypergraphPaths(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initalization

        # --------- Set up common hypergraph instances for testing ----------
        # Simple hypergraph
        self.simple_hypergraph = TimeVaryingHypergraph(
            hedges={'e1': ['v1', 'v2', 'v3'], 'e2': ['v2', 'v4'], 'e3': ['v5'], 'e4': []},
            timings={'e1': 1, 'e2': 2, 'e3': 3, 'e4': 4}
        )

        # Conflicting hypergraph
        self.conflicting_hypergraph = TimeVaryingHypergraph(
            hedges = {
                'e1': ['v1', 'v2'],
                'e2': ['v1', 'v3'],
                'e3': ['v2', 'v4'],
                'e4': ['v3', 'v4'],
                'e5': ['v4', 'v5'],
                'e6': ['v1', 'v5'],
            },
            timings = {
                'e1': timedelta(days=1),
                'e2': timedelta(days=1),
                'e3': timedelta(days=2),
                'e4': timedelta(days=3),
                'e5': timedelta(days=2),
                'e6': timedelta(days=4),
            }
        )

    def test_empty_graph(self):
        """
        Tests the behaviour of an empty graph

        Checks if the correct excpetions are raised when using an empty graph,
        one with hyperedges and one with vertices.

        Raises:
            EntityNotFound: If the sought after entity is not found in the hypergraph
        """

        # Arrange
        empty_hypergraph = TimeVaryingHypergraph({}, {})

        # Act and Assert
        with self.assertRaises(EntityNotFound):
            single_source_dijkstra_hyperedges(
                empty_hypergraph, 'v1', DistanceType.FASTEST)

        with self.assertRaises(EntityNotFound):
            single_source_dijkstra_vertices(
                empty_hypergraph, 'v1', DistanceType.FASTEST)

    def test_isolated_vertices(self):
        """
        Tests the behaviour of a hypergraph with an isolated vertex.

        Checks the behaviour of the single source dijkstra alogrithm when the graph
        contains an isolated vertex. It uses the two functions
        "single_source_dijsktra_hyperedges" and "single_source_dijkstra_vertices" 
        and verifies if they return the expected results with assertEqual.

        """

        # Arrange
        isolated_vertex = 'v5'
        expected_result = {}

        # Act
        result_hyperedges = single_source_dijkstra_hyperedges(
            self.simple_hypergraph, isolated_vertex, DistanceType.SHORTEST, min_timing=0)
        result_vertices = single_source_dijkstra_vertices(
            self.simple_hypergraph, isolated_vertex, DistanceType.SHORTEST, min_timing=0)

        # Assert
        self.assertEqual(expected_result, result_hyperedges,
                         'Isolated vertex is not empty!')
        self.assertEqual(expected_result, result_vertices,
                         'Isolated vertex is not empty!')

        self.assertEqual(result_hyperedges, result_vertices,
                         'Dijkstras implementations not equal')

    def test_reachability_to_isolated_vertex(self):
        """
        Test reachability to isolated vertex using single-source Dijkstra algorithm.

        The test verifies that an isolated vertex is not reachable from any of the given source vertices.
        It performs the following steps:
        1. Arrange the isolated vertex and a list of source vertices.
        2. Iterate over the source vertices.
        3. Act by running the single_source_dijkstra_hyperedges function to compute the traversal results.
        4. Assert that the isolated vertex is not present in the traversal results.
        """

        # Arrange
        isolated_vertex = 'v5'
        vertices = ['v1', 'v2', 'v3', 'v4']

        for vertex in vertices:
            # Act
            result_hyperedges = single_source_dijkstra_hyperedges(self.simple_hypergraph, vertex, DistanceType.SHORTEST, min_timing=0)

            # Assert
            self.assertNotIn(isolated_vertex, result_hyperedges, 'Isolated vertex was present in traversal!')


    def test_different_distance_types_on_simple_graph(self):
        """
        Tests different distances on a simple graph
        
        Tests the single_source_dijkstra_hyperedges function with different
        distance types (Shortest,Fastest and Foremost). It then verifies the
        results for each distance and if the hyperedge and vertex function
        has equivelent results.
        """

        # Arrange
        source_vertex = 'v1'
        expected_shortest = {'v2': 1, 'v3': 1, 'v4': 2}
        expected_fastest = {'v2': 0, 'v3': 0, 'v4': 1}
        expected_foremost = {'v2': 1, 'v3': 1, 'v4': 2}

        # Act
        result_shortest = single_source_dijkstra_hyperedges(self.simple_hypergraph, source_vertex, DistanceType.SHORTEST, min_timing=0)
        result_fastest = single_source_dijkstra_hyperedges(self.simple_hypergraph, source_vertex, DistanceType.FASTEST, min_timing=0)
        result_foremost = single_source_dijkstra_hyperedges(self.simple_hypergraph, source_vertex, DistanceType.FOREMOST, min_timing=0)

        # Assert
        self.assertEqual(expected_shortest, result_shortest)
        self.assertEqual(expected_fastest, result_fastest)
        self.assertEqual(expected_foremost, result_foremost)

        # Assert equivalence between the two implementations
        self.assertEqual(result_shortest, single_source_dijkstra_vertices(
            self.simple_hypergraph, source_vertex, DistanceType.SHORTEST, min_timing=0))
        self.assertEqual(result_fastest, single_source_dijkstra_vertices(
            self.simple_hypergraph, source_vertex, DistanceType.FASTEST, min_timing=0))
        self.assertEqual(result_foremost, single_source_dijkstra_vertices(
            self.simple_hypergraph, source_vertex, DistanceType.FOREMOST, min_timing=0))

    def test_shortest_distance_with_conflicting_timings(self):
        """
        Test the computation of shortest distance with conflicting timings using Dijkstra's algorithm.

        The test checks the correctness of the shortest distance computation when there are conflicting timings.
        It performs the following steps:
        1. Choose the source vertex.
        2. Manually compute the expected shortest distance based on the hypergraph structure and timings.
        3. Run Dijkstra's algorithm for shortest distance on the conflicting hypergraph.
        4. Assert that the computed shortest distance matches the expected shortest distance.
        5. Also, assert that the result from the hyperedges-based approach matches the result from the vertices-based approach.
        """

        # Choose the source and destination vertices
        source_vertex = 'v1'

        # Compute the expected shortest and fastest distances
        # Manually compute the distances based on the hypergraph structure and timings
        expected_shortest_distance = {'v2': 1, 'v3': 1, 'v4': 2, 'v5': 1}

        # Run Dijkstra's algorithm for shortest distance
        result_shortest = single_source_dijkstra_hyperedges(self.conflicting_hypergraph, source_vertex, DistanceType.SHORTEST, min_timing=0)
    
        self.assertEqual(result_shortest, expected_shortest_distance)
        self.assertEqual(result_shortest, single_source_dijkstra_vertices(self.conflicting_hypergraph, source_vertex, DistanceType.SHORTEST, min_timing=0))

    def test_fastest_distance_with_conflicting_timings(self):
        """
        Test the computation of fastest distance with conflicting timings using Dijkstra's algorithm.

        The test verifies the correctness of the fastest distance computation when there are conflicting timings.
        It performs the following steps:
        1. Choose the source vertex.
        2. Manually compute the expected fastest distance based on the hypergraph structure and timings.
        3. Run Dijkstra's algorithm for fastest distance on the conflicting hypergraph.
        4. Assert that the computed fastest distance matches the expected fastest distance.
        5. Also, assert that the result from the hyperedges-based approach matches the result from the vertices-based approach.
        """

        # Choose the source and destination vertices
        source_vertex = 'v1'

        # Compute the expected shortest and fastest distances
        # Manually compute the distances based on the hypergraph structure and timings
        expected_fastest_distance = {'v2': timedelta(0), 'v3': timedelta(0),
                                    'v4': timedelta(days=1), 'v5': timedelta(0)}

        # Run Dijkstra's algorithm for fastest distance
        result_fastest = single_source_dijkstra_hyperedges(self.conflicting_hypergraph, source_vertex, DistanceType.FASTEST)

        self.assertEqual(result_fastest, expected_fastest_distance)
        self.assertEqual(result_fastest, single_source_dijkstra_vertices(self.conflicting_hypergraph, source_vertex, DistanceType.FASTEST))
