import unittest
import hashlib
import importlib
import os
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from matplotlib.colorbar import cm
from tqdm.notebook import tqdm

class TestNotebookPlot(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization
        if os.path.isfile('data/minimal_paths/microsoft.pickle.bz2'):
            import notebooks.plot as notebookfile
            
            self.notebook = importlib.import_module(notebookfile)
        else:
            self.notebook = None

    def test_graph_consistency(self):
        if self.notebook is None:
            self.skipTest("Skipping graph consistency test as the file does not exist")
        else:
            # Repeat the notebook code multiple times
            num_iterations = 10
            stored_graph_hashes = []
        
            for i in range(num_iterations):
                # Execute the notebook code
                fig, axes = self.notebook.generate_notebook_graph()
                
                graph_filename = f'graph_{i}.png'
                plt.savefig(graph_filename)
                plt.close()
                
                # Calculate the hash of the generated graph image
                with open(graph_filename, 'rb') as f:
                    graph_data = f.read()
                    graph_hash = hashlib.sha256(graph_data).hexdigest()
                
                # Store the graph hash for comparison
                stored_graph_hashes.append(graph_hash)

            # Check for consistency
            consistent = all(hash_val == stored_graph_hashes[0] for hash_val in stored_graph_hashes)
            self.assertTrue(consistent, "The graph generation is not consistent.")

    def test_compute(self):
        if self.notebook is None:
            self.skipTest("Skipping graph consistency test as the file does not exist")
        else:
            # Prepare test data
            fastest = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
            target = ['A', 'B', 'C'] * 10  # Adjust the length as needed

            df = pd.DataFrame({
                'fastest': fastest[:len(target)],
                'target': target
            })

            # Call the compute function
            result = self.notebook.compute(df)

            # Perform assertions on the result
            self.assertIsInstance(result, pd.DataFrame)  # Ensure the result is a DataFrame
            # Add more assertions as needed to validate the expected output
