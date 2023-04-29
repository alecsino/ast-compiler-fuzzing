from modules.compiler import Compiler, Stats
from modules.test import FuzzedTest, Test
from tqdm import tqdm
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
        list_of_fuzzed_tests = [test for test in self.tests]
        interesting_tests: list[Stats] = []
                    
        while (n_file_found < self.n_threshold):
                with mp.Pool(self.num_cores) as pool:
                        with tqdm(total=len(self.tests)) as pbar:
                            for test in pool.imap_unordered(self.compiler.compile_test, [(test, self.mutate(test, test.inputs)) for test in list_of_fuzzed_tests]):
                                pbar.update()
                                if test.stats.n_tests() > 1 and test.stats.is_interesting():
                                    list_of_fuzzed_tests.append(test.test)
                                    interesting_tests.append(test.stats)
                                    n_file_found += 1
                                    
                            pbar.close()
        
        return interesting_tests
                            
    def mutate(self, test, inputs):
        """Mutate the test inputs.

        Args:
            test (Test): the test to mutate 
            inputs (list[Input]): the inputs to mutate
            
        Returns:
            Test: the mutated test
        """
        
        file_content = test.file_pattern

        for i, input in inputs.items():
            array = f"[{input.len}]" if input.len is not None else ""
            file_content = file_content.replace(f"[INPUT_{i}]", f'{input.name}{array} = {input.value}')
       
        return file_content