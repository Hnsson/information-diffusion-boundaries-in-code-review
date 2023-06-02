import unittest
import importlib
import io
import os
import hashlib


# For notebook generation
import pandas as pd
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
from matplotlib.colorbar import cm
import numpy as np
from tqdm.notebook import tqdm

from datetime import timedelta

class TestNotebookPlot(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization

        if os.path.exists(os.path.join(os.getcwd(), "data/minimal_paths/microsoft.pickle.bz2")):
            self.notebook = importlib.import_module("ipynb.fs.full.notebooks.plot")
        else:
            self.notebook = None

    def test_compute(self):
        if self.notebook is None:
            self.skipTest("Data not available")
        
        # Act
        test = pd.read_pickle(os.path.join(os.getcwd(), "data/minimal_paths/microsoft.pickle.bz2"))
        result = self.notebook.compute(test)

        # Arrange
        # Get the unique values from the test DataFrame's source column
        test_unique_values = test.index.get_level_values(0).unique()
        # Get the unique values from the first level of the column index
        result_categories = result.columns.get_level_values(0).unique()

        # Assert
        self.assertEqual(test_unique_values.categories.tolist(), result_categories.tolist())

    def copy_compute(self, df):
        cumulative_distribution_over_time = []
        total = len(df.index.get_level_values(0).categories)
        for source, group in tqdm(df.fastest.groupby(level=0), total=total):
            n_unique = group.reset_index(level=1).resample(pd.Timedelta(days=1), on='fastest', offset=-group.min()).target.nunique()
            cumulative_distribution_over_time += [n_unique.rename(source)]
        index = pd.timedelta_range(start=timedelta(weeks=0), end=timedelta(weeks=4), freq='D')
        return pd.concat(cumulative_distribution_over_time, axis=1).fillna(0).cumsum().reindex(index).ffill().astype(int)

    def test_copy_compute(self):
        if self.notebook is None:
            self.skipTest("Data not available")
        # Act
        test = pd.read_pickle(os.path.join(os.getcwd(), "data/minimal_paths/microsoft.pickle.bz2"))
        result = self.copy_compute(test)

        # Arrange
        # Get the unique values from the test DataFrame's source column
        test_unique_values = test.index.get_level_values(0).unique()
        # Get the unique values from the first level of the column index
        result_categories = result.columns.get_level_values(0).unique()

        # Assert
        self.assertEqual(test_unique_values.categories.tolist(), result_categories.tolist())

    def copy_generate_notebook(self):
        microsoft = pd.read_pickle('../data/minimal_paths/microsoft.pickle.bz2')


        ecdfs_over_time = self.notebook.compute(microsoft)


        fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True, sharex=True, sharey=False)

        df = ecdfs_over_time.reset_index(drop=True)
        x = df.index

        norm = cm.colors.Normalize(vmin=0.0, vmax=50)
        q = np.column_stack((np.linspace(0.99, 0.51, 49), np.linspace(0.01, 0.49, 49)))
        ax.fill_between(x=x, y1=0, y2=1, color=cm.plasma(norm(0)), edgecolor=None)
        for c, (l,u) in enumerate(q):
            y1 = df.quantile(l, axis=1).rename(l)
            y2 = df.quantile(u, axis=1).rename(u)
            color = cm.plasma(norm(c))
            for_cbar = ax.fill_between(x=x, y1=y1, y2=y2, color=color, edgecolor=None)

        df.median(axis=1).plot(ax=ax, color='white')

        ax.set_xlim(0, df.index.max())
        ax.set_ylim((0, df.shape[1]))
        ax.set_facecolor(cm.jet(norm(0)))

        ax.set_ylabel('Reachable participants')

        ax.set_xticks([0, 7, 14, 21, 28])
        ax.set_xticklabels([0, 7, 14, 21, 28])
        ax.minorticks_off()
        ax.set_title('Microsoft')

        ax_m = ax.twinx() # mirror the x-axis
        ax_m.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]);
        ax_m.set_ylabel('Network coverage')
        ax.set_xlabel('Time (days)')

        ax.yaxis.set_label_coords(-0.15, 0.5)
        ax.axhline(df.shape[1]/2)

        return fig, ax

    def test_graph_consistency(self):
        if self.notebook is None:
            self.skipTest("Data not available")
        # Repeat the notebook code multiple times
        num_iterations = 10
        stored_graph_hashes = []

        for i in range(num_iterations):
            # Execute the notebook code
            fig, axes = self.copy_generate_notebook_graph()

            # Capture the plot as binary data in memory
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            # Calculate the hash of the generated graph image
            graph_data = buffer.getvalue()
            graph_hash = hashlib.sha256(graph_data).hexdigest()

            # Close the plot
            plt.close(fig)

            # Store the graph hash for comparison
            stored_graph_hashes.append(graph_hash)

        # Check for consistency
        consistent = all(hash_val == stored_graph_hashes[0] for hash_val in stored_graph_hashes)
        self.assertTrue(consistent, "The graph generation is not consistent.")