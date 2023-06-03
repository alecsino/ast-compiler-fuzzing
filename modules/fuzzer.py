from modules.compiler import Compiler, Stats
from modules.strategies.mutator import Mutator
from modules.data_loader import DataLoader
from modules.test import FuzzedTest, Input, Test
from tqdm import tqdm
import multiprocessing as mp
import copy
import traceback

    
class Fuzzer:
    """The fuzzer."""
    
    def __init__(self, tests: list[Test], compiler: Compiler, mutator: Mutator, data_loader: DataLoader, num_cores: int, n_threshold: int = 10):
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
        list_of_fuzzed_tests = [FuzzedTest(test=test, mutated_inputs={i: copy.deepcopy(input) for i, input in test.inputs.items()}, stats=None) for test in self.tests if test.has_valid_inputs()]

        best_mutations: FuzzedTest = []
        interesting_tests: list[Stats] = []
        print(f"Start fuzzing {len(list_of_fuzzed_tests)} tests with {self.num_cores} cores. Threshold: {self.n_threshold}")

        pbar = tqdm(total=self.n_threshold)
        n_file_found = 0
        try:
            while True:
                    with mp.Pool(self.num_cores) as pool:
                            best_mutations = pool.imap_unordered(self._single_mutation, list_of_fuzzed_tests)
                            inner_bar = tqdm(total=len(list_of_fuzzed_tests), leave=False, desc="Mutating tests")
                            for test in best_mutations:
                                inner_bar.update()
                                if test is not None:
                                    pbar.update()
                                    n_file_found += 1
                                    pbar.set_description(f"Found new mutation: {test.test.name} with {test.stats.max_rateo[0]}")
                                    self.data_loader.save_results(test.stats)
                                    interesting_tests.append(test.stats)

                                    if n_file_found >= self.n_threshold:
                                        pbar.close()
                                        inner_bar.close()
                                        return interesting_tests

                            
                            list_of_fuzzed_tests = [ test for test in list_of_fuzzed_tests if test.test.name  not in [stat.file_path for stat in interesting_tests]]
                            inner_bar.close()
                            
        except KeyboardInterrupt:
            pass
        except Exception as e:
            traceback.print_exc()
        finally:     
            pbar.close()
            return interesting_tests
    
    def _single_mutation(self, fuzzed_test: FuzzedTest):
        """
        Perform a single round of mutation on a file.
        """
        
        # check without mutation if the test is interesting
        try:
            no_mut = self.compiler.compile_test((fuzzed_test.test, self.apply(fuzzed_test.test, fuzzed_test.test.inputs), fuzzed_test.mutated_inputs))
            if no_mut.stats.is_interesting() and no_mut.is_asan_safe(self.compiler):
                return no_mut

            fuzzed = self._find_best_mutations(fuzzed_test, n_iterations=50)
            if fuzzed is None:
                return None
            
            # reduction
            fuzzed = self._reduce_test(fuzzed)
            
            if fuzzed.stats.is_interesting():
                fuzzed.stats.strategy_mutation = "Random"
                return fuzzed
            
            for i in fuzzed.mutated_inputs:
                if fuzzed.mutated_inputs[i].interesting:
                    for strategy in self.mutator.strategies:
                        for n in range(self.mutator.STRATEGY_TRIES[strategy]):
                    
                            fuzzed.mutated_inputs[i].value = self._mutate_input(fuzzed.mutated_inputs[i])
                            fuzzed = self.compiler.compile_test((fuzzed.test, self.apply(fuzzed.test, fuzzed.mutated_inputs), fuzzed.mutated_inputs))
                                            
                            if fuzzed.stats.is_interesting() and fuzzed.is_asan_safe(compiler=self.compiler):
                                fuzzed.stats.strategy_mutation = strategy
                                return fuzzed
            return None
        except KeyboardInterrupt:
            return None

    
    def _reduce_test(self, fuzzed_test: FuzzedTest) -> FuzzedTest:
        """
        Reduce the test by removing the inputs that do not affect the result.
        """
        for i in fuzzed_test.mutated_inputs:
            
            new_inputs = copy.deepcopy(fuzzed_test.mutated_inputs)
            new_inputs[i].value = fuzzed_test.test.inputs[i].value
            new_fuzzed = self.compiler.compile_test((fuzzed_test.test, self.apply(fuzzed_test.test, new_inputs), new_inputs))
            if new_fuzzed.has_improved(fuzzed_test.stats):
                 fuzzed_test.mutated_inputs[i].interesting = False

        return fuzzed_test

    def _find_best_mutations(self, fuzzed_test: FuzzedTest, n_iterations = 100) ->  FuzzedTest:
        """
        Mutate a test n_iterations times and return the best mutation.
        """
        
        mutations = []
        for i in range(n_iterations):

            mutated_inputs = self.mutate_inputs(fuzzed_test)
            fuzzed_test = self.compiler.compile_test((fuzzed_test.test, self.apply(fuzzed_test.test, mutated_inputs), mutated_inputs))
            mutations.append(fuzzed_test)
            
        best_mutants = sorted(mutations, key=lambda x: x.stats.max_rateo[0])
        
        try_asan = 0
        while try_asan < 5:
            try_asan += 1
            best_mutant = best_mutants.pop()
            
            if best_mutant.stats.max_rateo[0] == 0:
                return None

            if best_mutant.is_asan_safe(self.compiler):
                return best_mutant

        return None
        
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

    def mutate_inputs(self, test: FuzzedTest) -> dict[int, Input]:
        """
        Mutate the test inputs.
        
        Args:
            test (Test): the original test
            
        Returns:
            dict[Input]: the mutated inputs
        """
        
        new_inputs = test.mutated_inputs.copy()
        for i in range(len(test.mutated_inputs)):
                new_inputs[i].value = self._mutate_input(test.mutated_inputs[i])
        return new_inputs
    
    def _mutate_input(self, input: Input, strategy: str = "Random"):
        return self.mutator.mutate(input, strategy)
        