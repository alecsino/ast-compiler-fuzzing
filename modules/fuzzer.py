import random
from modules.compiler import Compiler, Stats
from modules.strategies.mutator import Mutator
from modules.test import FuzzedTest, Input, Test
from modules import constants
from tqdm import tqdm
import multiprocessing as mp

class Fuzzer:
    """The fuzzer."""
    
    def __init__(self, tests: list[Test], compiler: Compiler, mutator: Mutator,  num_cores: int, n_threshold: int = 10, data_loader = None):
        self.tests = tests
        self.compiler = compiler
        self.num_cores = num_cores
        self.n_threshold = n_threshold
        self.mutator = mutator
        self.data_loader = data_loader
    
    def fuzz(self):
        """
        Fuzz the tests.
            
        Returns:
            Test: the interesting tests
        """  
              
        n_file_found = 0 
        depth = 0
        breadth = 0
        list_of_fuzzed_tests = [(test, test.inputs, depth, breadth) for test in self.tests if test.has_valid_inputs()] # start the seed with the original tests
        
        interesting_tests: list[Stats] = []
        n_iteration = 0
        print(f"Start fuzzing {len(list_of_fuzzed_tests)} tests with {self.num_cores} cores. Threshold: {self.n_threshold}")

        pbar = tqdm(total=self.n_threshold)
        try:
            while (n_iteration < 1 and n_file_found < self.n_threshold):
                    with mp.Pool(self.num_cores) as pool:
                            fuzzed_tests = pool.imap_unordered(self.compiler.compile_test, [(test, self.apply(test, test.inputs), mutated_inputs, depth, breadth ) for test, mutated_inputs, depth, breadth in list_of_fuzzed_tests])
                            n_iteration += 1
                            list_of_fuzzed_tests = []
                            for fuzzed_test in fuzzed_tests:
                                tqdm.write(fuzzed_test.test.name)
                                if fuzzed_test.stats.n_tests > 1 and fuzzed_test.stats.is_interesting():

                                    if fuzzed_test.stats.max_rateo[0] > 1.50:
                                        tqdm.write(f"Checking {fuzzed_test.test.name}")

                                        if fuzzed_test.is_asan_safe(self.compiler):
                                            pbar.update()
                                            n_file_found += 1
                                            pbar.set_description(f"Found new mutation: {fuzzed_test.test.name}")
                                            self.data_loader.save_results(fuzzed_test.stats)
                                            interesting_tests.append(fuzzed_test.stats)
                                            continue
                                        else:
                                            tqdm.write(f"Mutation for {fuzzed_test.test.name} is not ASAN safe")

                                    list_of_fuzzed_tests.append((fuzzed_test.test, self.mutate_inputs(fuzzed_test,
                                                                                                    fuzzed_test.depth + 1, 
                                                                                                    fuzzed_test.breadth) , fuzzed_test.depth + 1, fuzzed_test.breadth))
                                    
                                else:
                                    list_of_fuzzed_tests.append((fuzzed_test.test, self.mutate_inputs(fuzzed_test, 
                                                                                                    fuzzed_test.depth, 
                                                                                                    fuzzed_test.breadth + 1), fuzzed_test.depth, fuzzed_test.breadth + 1))
                            self.mutator.plot()
        except KeyboardInterrupt:
             pass
        finally:     
            pbar.close()
            return interesting_tests
                            
    def apply(self, test: Test, inputs: dict[int, Input]) -> str:
        """
        Apply to the test the inputs.

        Args:
            test (Test): the test to mutate 
            inputs (list[Input]): the inputs to mutate
            
        Returns:
            str: the mutated test content
        """
        
        file_content = test.file_pattern

        for i, input in inputs.items():
            array = f"[{input.len}]" if input.len is not None else ""
            file_content = file_content.replace(f"[INPUT_{i}]", f'{input.name}{array} = {input.value}')
    
        return file_content

    def mutate_inputs(self, test: FuzzedTest, depth: int, breadth: int) -> dict[int, Input]:
        """
        Mutate the test inputs.
        NOTE: the mutation is either done vertically or horizontally.
        
        Args:
            test (Test): the original test
            inputs (list[Input]): the inputs to the fuzzed test to mutate
            
        Returns:
            list[Input]: the mutated inputs
        """
        
        left_most = len(test.mutated_inputs) - 1 
        new_inputs = test.mutated_inputs.copy()
        
        if depth != test.depth:
             new_inputs[left_most].value = self.mutator.mutate(test.mutated_inputs[left_most])
        else:
             new_inputs[(left_most - breadth + len(test.mutated_inputs)) % len(test.mutated_inputs)].value = self.mutator.mutate(test.mutated_inputs[(left_most - breadth + len(test.mutated_inputs))% len(test.mutated_inputs)])
        
        return new_inputs
    