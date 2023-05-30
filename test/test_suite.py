import sys
import unittest

from test_model import TestCommunicationNetwork, TestTimeVaryingHypergraph
from test_minimal_paths import TestMinimalPath, TestHypergraphPaths


class TestSuite():
    def __init__(self, test_cases=[]):
        self.command_mapping = {
            'hg': TestTimeVaryingHypergraph,
            'mp': TestMinimalPath,
            'hgp': TestHypergraphPaths,
            'cn': TestCommunicationNetwork
        }
        
        self.suite = self.setup_suite(test_cases)

    def setup_suite(self, test_cases):
        test_suite = unittest.TestSuite()

        if not test_cases:
            test_cases = self.command_mapping.keys()

        for command in test_cases:
            test_case_class = self.command_mapping.get(command)
            if test_case_class:
                test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_case_class))

        # test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTimeVaryingHypergraph))
        # test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMinimalPath))
        # test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestHypergraphPaths))
        # test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCommunicationNetwork))

        return test_suite

    def run(self):
        unittest.TextTestRunner().run(self.suite)

if __name__ == '__main__':
    TestSuite(sys.argv[1:]).run()
