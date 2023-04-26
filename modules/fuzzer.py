from modules.compiler import Compiler
from modules.test import FuzzedTest, Test

import multiprocessing as mp

class Fuzzer:
    """The fuzzer."""
    
    def __init__(self, tests: list[Test], compiler: Compiler, num_cores: int, n_threshold: int = 10):
        self.tests = tests
        self.compiler = compiler
        self.num_cores = num_cores
        self.n_threshold = n_threshold
    
    def fuzz(self):
        """Fuzz the tests."""  
              
        n_file_found = 0
        
        # init
        list_of_fuzzed_tests = [ self.seed_file(test) for test in self.tests]
                    
        while (n_file_found < self.threshold):
                with mp.Pool(self.num_cores) as pool:
                        for test in pool.imap_unordered(self.compiler.compile_test, [test for test in list_of_fuzzed_tests]):
                            if test.stats is not None and self._is_interesting(test.stats):
                                list_of_fuzzed_tests += self.mutate(test)
                                
                            
    def mutate(self, test):
        """Mutate the test inputs.

        Args:
            test (Test): the test to mutate 
            
        Returns:
            Test: the mutated test
        """
                                
    def seed_file(self, test):
        """Seed the test files with boundary values.
        
        Args:
            test (Test): the test to mutate 
        
        Returns:
            Test: the seeded test
        """
    
    def _is_interesting(self, stats):
        """Whether the ratio with respect to an older version is greater than 1.

        Args:
            stats (dict[str, Any]): the stats of the test

        Returns:
            bool: whether the test is interesting
        """
        
        min_v = min([value for key, value in stats.items() if not key.startswith("file") and not key.startswith("last")])
        stats["max_rateo"] = round(stats["last"] / min_v, 2)
        if stats["max_rateo"] > 1:
            return True
        
        return False