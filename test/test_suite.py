import unittest

from test_model import TestCommunicationNetwork, TestTimeVaryingHypergraph
from test_minimal_paths import TestMinimalPath


class TestSuite():
    def __init__(self):
        self.suite = self.setup_suite()

    def setup_suite(self):
        test_suite = unittest.TestSuite()

        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTimeVaryingHypergraph))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMinimalPath))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCommunicationNetwork))

        return test_suite

    def run(self):
        unittest.TextTestRunner().run(self.suite)

if __name__ == '__main__':
    TestSuite().run()
