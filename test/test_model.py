import sys
sys.path.append("..")  # Add parent directory to the system path

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

    def test_cn_hyperedges(self):
        """
        Test the CommunicationNetwork (hypergraph) for its channels (hyperedges)
        """

        # Right amount of hyperedges (channels)
        self.assertEqual(len(self.cn.hyperedges()), 3)

        # Right hyperedges (channels)
        self.assertEqual(self.cn.hyperedges(), {'h1', 'h3', 'h2'})

        # Right vertice (participants) when called with specific hyperedge (channels)
        self.assertEqual(self.cn.hyperedges('v1'), {'h1'})
        self.assertEqual(self.cn.hyperedges('v2'), {'h2', 'h1'})
        self.assertEqual(self.cn.hyperedges('v3'), {'h3', 'h2'})

        # Test with empty or wrong hyperedge (channel)
        with self.assertRaises(EntityNotFound):
            self.cn.hyperedges('xx')

    def test_cn_vertices(self):
        """
        Test the CommunicationNetwork (hypergraph) for its vertices (participants)
        """

        # Right amount of vertices (participants)
        self.assertEqual(len(self.cn.vertices()), 4)

        # Right vertices (participants)
        self.assertEqual(self.cn.vertices(), {'v1', 'v2', 'v3', 'v4'})

        # Right hyperedge (channels) when called with specific vertice (participant)
        self.assertEqual(self.cn.vertices('h1'), {'v1', 'v2'})
        self.assertEqual(self.cn.vertices('h2'), {'v2', 'v3'})
        self.assertEqual(self.cn.vertices('h3'), {'v3', 'v4'})

        # Test with empty or wrong hyperedge (channel)
        with self.assertRaises(EntityNotFound):
            self.cn.vertices('xx')

    @patch('pathlib.Path.open', new_callable=mock_open)
    def test_load_json(self, mock_file_open):
        # Arrange
        json_mock_data = {
            'channel1': {'participants': ['participant_1', 'participant_2'], 'end': '2023-05-27'},
            'channel2': {'participants': ['participant_3', 'participant_4'], 'end': '2023-05-28'}
        }

        json_mock_content = json.dumps(json_mock_data)
        mock_file_open.return_value.read.return_value = bz2.compress(json_mock_content)

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
        cn = CommunicationNetwork.from_json('../data/networks/microsoft.json.bz2')
        self.assertEqual(len(cn.participants()), 37103)
        self.assertEqual(len(cn.channels()), 309740)

        self.assertEqual(len(cn.vertices()), 37103)
        self.assertEqual(len(cn.hyperedges()), 309740)


class TestTimeVaryingHypergraph(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization

    # def test_bla(self):
        pass
