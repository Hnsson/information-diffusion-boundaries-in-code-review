import sys
from os.path import dirname, abspath

# Add the parent directory to the module search path
parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

import unittest
from unittest.mock import patch, mock_open, ANY
from pathlib import Path
from datetime import datetime
import bz2

import os

try:
    import orjson as json
except ImportError:
    import json

from simulation.model import CommunicationNetwork, TimeVaryingHypergraph, EntityNotFound

class TestCommunicationNetwork(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization
        self.cn = CommunicationNetwork({'h1': ['v1', 'v2'], 'h2': ['v2', 'v3'], 'h3': ['v3', 'v4']}, {'h1': 1, 'h2': 2, 'h3': 3})

    def test_cn_channels(self):
        """
        Test the CommunicationNetwork (hypergraph) for its channels (hyperedges)
        """

        # Right amount of hyperedges (channels)
        self.assertEqual(len(self.cn.channels()), 3)

        # Right hyperedges (channels)
        self.assertEqual(self.cn.channels(), {'h1', 'h3', 'h2'})

        # Right vertice (participants) when called with specific hyperedge (channels)
        self.assertEqual(self.cn.channels('v1'), {'h1'})
        self.assertEqual(self.cn.channels('v2'), {'h2', 'h1'})
        self.assertEqual(self.cn.channels('v3'), {'h3', 'h2'})

        # Test with empty or wrong hyperedge (channel)
        with self.assertRaises(EntityNotFound):
            self.cn.channels('xx')

    def test_cn_vertices(self):
        """
        Test the CommunicationNetwork (hypergraph) for its vertices (participants)
        """

        # Right amount of vertices (participants)
        self.assertEqual(len(self.cn.participants()), 4)

        # Right vertices (participants)
        self.assertEqual(self.cn.participants(), {'v1', 'v2', 'v3', 'v4'})

        # Right hyperedge (channels) when called with specific vertice (participant)
        self.assertEqual(self.cn.participants('h1'), {'v1', 'v2'})
        self.assertEqual(self.cn.participants('h2'), {'v2', 'v3'})
        self.assertEqual(self.cn.participants('h3'), {'v3', 'v4'})

        # Test with empty or wrong hyperedge (channel)
        with self.assertRaises(EntityNotFound):
            self.cn.participants('xx')

    @patch('pathlib.Path.open', new_callable=mock_open)
    def test_load_json(self, mock_file_open):
        # Arrange
        json_mock_data = {
            'channel1': {'participants': ['participant_1', 'participant_2'], 'end': '2023-05-27'},
            'channel2': {'participants': ['participant_3', 'participant_4'], 'end': '2023-05-28'}
        }

        # json_mock_content = json.dumps(json_mock_data)
        # mock_file_open.return_value.read.return_value = bz2.compress(json_mock_content)
        json_bytes = {}
        try:
            json_bytes = json.dumps(json_mock_data).encode('utf-8')
        except AttributeError:
            json_bytes = json.dumps(json_mock_data)

        mock_file_open.return_value.read.return_value = bz2.compress(json_bytes)

        file_path = './data/networks/fake.json.bz2'

        # Act
        cn = CommunicationNetwork.from_json(file_path)

        # Assert
        mock_file_open.assert_called_once_with('rb')
        mock_file_open.return_value.read.assert_called_once()

        excepted_hyperedges = set(json_mock_data.keys())
        self.assertEqual(cn.hyperedges(), excepted_hyperedges)
        expected_vertices = set([participant for channel_data in json_mock_data.values() for participant in channel_data['participants']])
        self.assertEqual(cn.vertices(), expected_vertices)
        expected_timings = {'channel1': datetime.fromisoformat(json_mock_data['channel1']['end']), 'channel2': datetime.fromisoformat(json_mock_data['channel2']['end'])}
        self.assertEqual(cn.timings(), expected_timings)

    def test_cn_with_data(self):
        cn = CommunicationNetwork.from_json('data/networks/microsoft.json.bz2')
        self.assertEqual(len(cn.participants()), 37103)
        self.assertEqual(len(cn.channels()), 309740)

        self.assertEqual(len(cn.vertices()), 37103)
        self.assertEqual(len(cn.hyperedges()), 309740)


class TestTimeVaryingHypergraph(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization

    def test_vertices(self):
        hedges = {'e1': ['a', 'b'], 'e2': ['a', 'c', 'd'], 'e3': ['c', 'd', 'e'], 'e4': [], '': ['f'], 'e5': ['g']}
        timings = {'e1': 1, 'e2': 2, 'e3': 2, 'e4': 3, '': 4, 'e5': 5}

        hyper_graph = TimeVaryingHypergraph(hedges, timings)

        # Are all vertices present? -> Should be {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
        all_vertices = hyper_graph.vertices()
        expected_vertices = {vertex for hedge_vertices in hedges.values() for vertex in hedge_vertices}
        self.assertEqual(all_vertices, expected_vertices, 'All vertices is not present!')

        # Is the order correct? Should be -> Should be 7
        self.assertEqual(len(all_vertices), len(expected_vertices), 'The order is not correct')

        # What vertices are incident to edge 'e3'? -> Should be {'c', 'd', 'e'}
        hedge = 'e3'
        hedge_vertices = hyper_graph.vertices(hedge)
        expected_hyperedge_vertices = set(hedges[hedge])
        self.assertEqual(hedge_vertices, expected_hyperedge_vertices, f'All vertices are not present in hedge: {hedge}!')

        # Test with unknown hyperedge. -> Should Raise EntityNotFound
        unknown_hedge = 'e10'
        with self.assertRaises(EntityNotFound):
            hyper_graph.vertices(unknown_hedge)
        
        # Isolated vertex: A vertex v is isolated if E(v) = ∅
        null_hedge = {''}
        isolated_vertex = 'f'
        isolated_hedge = hyper_graph.hyperedges(isolated_vertex)
        self.assertEqual(isolated_hedge, null_hedge, 'Hyperedges to a isolated vertex should be null (∅)')


        # Pendant vertex: A vertex is incident to exactly 1 edge
        pendant_vertex = 'g'
        incident_edges = len(hyper_graph.hyperedges(pendant_vertex))
        self.assertEqual(incident_edges, 1, f'A pendant vertex: {pendant_vertex} must be incident to exactly 1 edge')
    
    def test_hedges(self):
        hedges = {'e1': ['a', 'b'], 'e2': ['a', 'c', 'd'], 'e3': ['c', 'd', 'e'], 'e4': [], '': ['f'], 'e5': ['g']}
        timings = {'e1': 1, 'e2': 2, 'e3': 2, 'e4': 3, '': 4, 'e5': 5}

        hyper_graph = TimeVaryingHypergraph(hedges, timings)

        # Are all hedges present? -> Should be {'e1', 'e2', 'e3', 'e4', '', 'e5'}
        all_hedges = hyper_graph.hyperedges()
        expected_hedges = set(hedges.keys())
        self.assertEqual(all_hedges, expected_hedges, 'All hedges are not present!')

        # Is the size correct? -> Should be 6
        self.assertEqual(len(all_hedges), len(expected_hedges), 'The size is not correct')

        # What edges are incident to vertex 'd'? -> Should be {'e2', 'e3'}
        vertex = 'd'
        incident_hedges = hyper_graph.hyperedges(vertex)
        expected_incident_hedges = set(h for h, vertices in hedges.items() if vertex in vertices)
        self.assertEqual(incident_hedges, expected_incident_hedges, f'Incident edges to vertex: {vertex} does not match')

        # Test with unknown vertex. -> Should Raise EntityNotFound
        unknown_vertex = 'z'
        with self.assertRaises(EntityNotFound):
            hyper_graph.hyperedges(unknown_vertex)
        
        # Empty edge: An edge is empty is e = ∅
        empty_edge = 'e4'
        empty_vertices = hyper_graph.vertices(empty_edge)
        null_vertices = set()
        self.assertEqual(empty_vertices, null_vertices, f'An empty edge {empty_edge} should contain empty vertices i.e. e = ∅')

        # Singleton: An edge incident to exactly 1 vertex
        singleton_hedge = 'e5'
        incident_vertices = len(hyper_graph.vertices('e5'))
        self.assertEqual(incident_vertices, 1, f'A singleton hedge {singleton_hedge} should only be incident to exactly 1 vertex')
    
    def test_timings(self):
        hedges = {'e1': ['a', 'b'], 'e2': ['a', 'c', 'd'], 'e3': ['c', 'd', 'e'], 'e4': [], '': ['f'], 'e5': ['g']}
        timings = {'e1': 1, 'e2': 2, 'e3': 2, 'e4': 3, '': 4, 'e5': 5}

        hyper_graph = TimeVaryingHypergraph(hedges, timings)

        # Are all timings correct? -> Should be {'e1': 1, 'e2': 2, 'e3': 2, 'e4': 3, '': 4, 'e5': 5}
        all_timings = hyper_graph.timings()
        self.assertEqual(all_timings, timings, 'All timings does not equal expected timings!')

        # Is the timing for a specific hedge {'e1'} correct? -> Should be 1
        hedge = 'e1'
        hedge_timing = hyper_graph.timings(hedge)
        expected_timing = timings[hedge]
        self.assertEqual(hedge_timing, expected_timing, f'The hedge: {hedge} should have correct timing!')

        # Test timing unknown hedge. -> Should Raise EntityNotFound
        unknown_hedge = 'e10'
        with self.assertRaises(KeyError):
            hyper_graph.timings(unknown_hedge)

    def test_large_random_topology(self):
        """
        """
        import random
        # Arrange
        possible_hedges = ['e1','e2','e3','e4','e5','e6','e7','e8','e9','e10']
        possible_vertices = ['v1','v2','v3','v4','v5','v6','v7','v8','v9','v10']
        possible_timings = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        hedges = {}
        timings = {}

        for hedge in possible_hedges:
            hedges[hedge] = []
            for _ in range(random.randint(1, len(possible_vertices))):
                hedges[hedge].append(random.choice(possible_vertices))
            
            timings[hedge] = random.choice(possible_timings)

        # Act
        hypergraph = TimeVaryingHypergraph(hedges, timings)

        # Assert
        self.assertCountEqual(hypergraph.hyperedges(), possible_hedges)
        self.assertTrue(hypergraph.vertices().issubset(set(possible_vertices)))
        self.assertTrue(all(value in possible_timings for value in hypergraph.timings().values()))




    # IMPORTANT TERMINOLOGY FOR A HYPERGRAPH. NEED ALL TERMINOLOGY TO BE DEFINED AS A HYPERGRAPH
    # def test_wrong_vertex(self):
    #     hyper_graph = TimeVaryingHypergraph({'e1': ['a', 'b'], 'e2': ['a', 'c', 'd'], 'e3': ['c', 'd', 'e'], 'e4': [], '': ['f'], 'e5': 'g'}, {'h1': 1, 'h2': 2, 'h3': 3})

    #     # Order
    #     print(hyper_graph.vertices())

    #     # Edges
    #     print(hyper_graph.hyperedges())

    #     # What edges are incident to vertex 'd'? -> Should be {'e2', 'e3'}
    #     print(hyper_graph.hyperedges('d'))

    #     # What vertices are incident to edge 'e3'? -> Should be {'c', 'd', 'e'}
    #     print(hyper_graph.vertices('e3'))

    #     # Isolated vertex: A vertex v is isolated if E(v) = ∅
    #     print(hyper_graph.hyperedges('f'), '= {''}')

    #     # Empty edge: An edge is empty is e = ∅
    #     print(hyper_graph.vertices('e4'), '= set()')

    #     # Singleton
    #     print(len(hyper_graph.vertices('e5')), '= 1')

    #     # Pendant vertex
    #     print(len(hyper_graph.hyperedges('g')), '= 1')

    #     # This is a simple hypergraph due to not including edges i.e. an hyperedge that is a subset of another hyperedge
    #     # -------- #
