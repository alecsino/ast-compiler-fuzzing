from collections import defaultdict
import datetime
import random
from typing import NamedTuple
from modules.compiler import Compiler, Stats
from modules.data_analyzer import DataAnalyzer
from modules.data_loader import DataLoader
from modules.strategies.mutator import Mutator
from modules.test import FuzzedTest, Input, Test
from modules import constants
from tqdm import tqdm
import copy
import multiprocessing as mp
import traceback

FuzzedTestTuple = NamedTuple("FuzzedTestTuple", [("test", Test), ("old_inputs", dict[int, Input]), ("mutated_inputs", dict[int, Input]), ("depth", int), ("breadth", int), ("stats", Stats)])
    
class Fuzzer:
    """The fuzzer."""
    
    def __init__(self, tests: list[Test], compiler: Compiler, mutator: Mutator,  num_cores: int,  data_loader : DataLoader, data_analyzer : DataAnalyzer, n_threshold: int = 10):
        self.tests = tests
        self.compiler = compiler
        self.num_cores = num_cores
        self.n_threshold = n_threshold
        self.mutator = mutator
        self.data_loader = data_loader
        self.data_analyzer = data_analyzer
        
    def fuzz(self):
        """
        Fuzz the tests.
            
        Returns:
            Test: the interesting tests
        """  
              
        n_file_found = 0 
        depth = 0
        breadth = 0
        list_of_fuzzed_tests = [FuzzedTestTuple(test=test, old_inputs=test.inputs, mutated_inputs=test.inputs, depth=depth, breadth=breadth, stats=None) for test in self.tests if test.has_valid_inputs()] # start the seed with the original tests
        # list_of_fuzzed_tests = [(test, mutated_inputs, depth, breadth) for test, mutated_inputs, depth, breadth, _ in  self.find_best_inputs(list_of_fuzzed_tests, n_iteration=1)] # start the seed with the original tests
        
        interesting_tests: list[Stats] = []
        n_iteration = 0
        print(f"Start fuzzing {len(list_of_fuzzed_tests)} tests with {self.num_cores} cores. Threshold: {self.n_threshold}")

        pbar = tqdm(total=self.n_threshold)
        try:
            while n_file_found < self.n_threshold:
                    with mp.Pool(self.num_cores) as pool:
                            fuzzed_tests = pool.imap_unordered(self.compiler.compile_test, [(test, self.apply(test, test.inputs), old_inputs, mutated_inputs, depth, breadth, old_stats) for test, old_inputs, mutated_inputs, depth, breadth, old_stats in list_of_fuzzed_tests])
                            
                            n_iteration += 1
                            list_of_fuzzed_tests = []
                            for fuzzed_test in fuzzed_tests:
                                tqdm.write(fuzzed_test.test.name)
                                
                                if fuzzed_test.stats.n_tests > 1 and fuzzed_test.stats.is_interesting():
                                        self.data_analyzer.register_interesting_test(fuzzed_test.test.name, fuzzed_test.stats, datetime.datetime.now(), n_iteration)
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

                                if fuzzed_test.has_improved():
                                    self.data_analyzer.register_improvement(fuzzed_test.test.name, fuzzed_test.stats, fuzzed_test.old_stats, fuzzed_test.old_inputs, fuzzed_test.mutated_inputs)
                                    list_of_fuzzed_tests.append(FuzzedTestTuple(fuzzed_test.test, fuzzed_test.mutated_inputs, 
                                                                                self.mutate_inputs(fuzzed_test,
                                                                                                    fuzzed_test.depth + 1, 
                                                                                                    fuzzed_test.breadth + 1) ,  fuzzed_test.depth + 1, fuzzed_test.breadth  + 1, fuzzed_test.stats))
                                else:
                                    list_of_fuzzed_tests.append(FuzzedTestTuple(fuzzed_test.test,  fuzzed_test.mutated_inputs, self.mutate_inputs(fuzzed_test, 
                                                                                                    fuzzed_test.depth, 
                                                                                                    fuzzed_test.breadth + 1), fuzzed_test.depth, fuzzed_test.breadth + 1, fuzzed_test.stats))
        except KeyboardInterrupt:
             pass
        except Exception as e:
            traceback.print_exc()
        finally:     
            pbar.close()
            return interesting_tests
                            
    def find_best_inputs(self, list_of_fuzzed_tests: list, n_iteration: int = 100) -> list[Input]:
        
        print("Mutating the inputs of the tests to find the best inputs")
        
        tests = defaultdict(list)
        for i in range(n_iteration):
                with mp.Pool(self.num_cores) as pool:
                    with tqdm(total=len(list_of_fuzzed_tests)) as pbar:
                            for fuzzed_test in pool.imap_unordered(self.compiler.compile_test, [(test, self.apply(test, test.inputs), mutated_inputs, depth, breadth ) for test, mutated_inputs, depth, breadth in list_of_fuzzed_tests]):
                                tests[fuzzed_test.test.name].append((fuzzed_test.test, self.mutate_inputs(fuzzed_test) , fuzzed_test.depth, fuzzed_test.breadth, fuzzed_test.stats))
                                pbar.update()
                    pbar.close()
        return [max(tests[test], key=lambda x: x[4].max_rateo[0]) for test in tests]
    
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

    def mutate_inputs(self, test: FuzzedTest, depth: int | None= None, breadth: int | None= None) -> dict[int, Input]:
        """
        Mutate the test inputs.
        NOTE: the mutation is either done vertically or horizontally.
        
        Args:
            test (Test): the original test
            depth (int): the depth of the mutation. If None, mutate all the inputs
            breadth (int): the breadth of the mutation. If None, mutate all the inputs
            
        Returns:
            list[Input]: the mutated inputs
        """
        
        left_most = len(test.mutated_inputs) - 1 
        
        if depth is None or breadth is None: # mutate all the inputs
            new_inputs = test.mutated_inputs.copy()
            for i in range(len(test.mutated_inputs)):
                new_inputs[i].value = self.mutator.mutate(test.mutated_inputs[i])
        elif depth != test.depth: # mutate vertically
            new_inputs = test.mutated_inputs.copy() # progress with the mutated inputs of the previous iteration
            new_inputs[(left_most - breadth + len(test.mutated_inputs)) % len(test.mutated_inputs)].value =  self.mutator.mutate(test.mutated_inputs[(left_most - breadth + len(test.mutated_inputs))% len(test.mutated_inputs)])
        else: # mutate horizontally
            new_inputs = test.old_inputs.copy() # backtrack and progress with the previous inputs
            new_inputs[(left_most - breadth + len(test.mutated_inputs)) % len(test.mutated_inputs)].value = self.mutator.mutate(test.mutated_inputs[(left_most - breadth + len(test.mutated_inputs))% len(test.mutated_inputs)])
        
        return new_inputs
    