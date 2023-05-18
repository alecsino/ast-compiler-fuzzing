import random
from modules.compiler import Compiler, Stats
from modules.test import FuzzedTest, Input, Test
from modules import constants
from tqdm import tqdm
import multiprocessing as mp

class Fuzzer:
    """The fuzzer."""
    
    def __init__(self, tests: list[Test], compiler: Compiler, num_cores: int, n_threshold: int = 50):
        self.tests = tests
        self.compiler = compiler
        self.num_cores = num_cores
        self.n_threshold = n_threshold
    
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
        unique_files: list[str] = []
        n_iteration = 0
        while (n_iteration < 1 and n_file_found < self.n_threshold):
                with mp.Pool(self.num_cores) as pool:
                        with tqdm(total=len(list_of_fuzzed_tests)) as pbar:
                            fuzzed_tests = pool.imap_unordered(self.compiler.compile_test, [(test, self.apply(test, test.inputs), mutated_inputs, depth, breadth ) for test, mutated_inputs, depth, breadth in list_of_fuzzed_tests])
                            n_iteration += 1
                            list_of_fuzzed_tests = []
                            for fuzzed_test in fuzzed_tests:
                                pbar.update()
                                if fuzzed_test.stats.n_tests > 1 and fuzzed_test.stats.is_interesting():
                                    list_of_fuzzed_tests.append((fuzzed_test.test, self.mutate_inputs(fuzzed_test,
                                                                                                      fuzzed_test.depth + 1, 
                                                                                                      fuzzed_test.breadth) , fuzzed_test.depth + 1, fuzzed_test.breadth))
                                    
                                    if fuzzed_test.test.name not in unique_files:
                                        unique_files.append(fuzzed_test.test.name)
                                        n_file_found += 1 if fuzzed_test.stats.max_rateo[0] > 1.50 else 0
                                        # print(f"Found new file: {fuzzed_test.test.name}")
                                        interesting_tests.append(fuzzed_test.stats)
                                else:
                                    list_of_fuzzed_tests.append((fuzzed_test.test, self.mutate_inputs(fuzzed_test, 
                                                                                                      fuzzed_test.depth, 
                                                                                                      fuzzed_test.breadth + 1), fuzzed_test.depth, fuzzed_test.breadth + 1))
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
             new_inputs[left_most].value = self.random_value(test.mutated_inputs[left_most])
        else:
             new_inputs[(left_most - breadth + len(test.mutated_inputs)) % len(test.mutated_inputs)].value = self.random_value(test.mutated_inputs[(left_most - breadth + len(test.mutated_inputs))% len(test.mutated_inputs)])
        
        return new_inputs
    
    def random_value(self, input: Input) -> str:
        """
        Generate a random value for the input.
        
        Args:
            input (Input): the inputs to generate a random value for
            
        Raises:
            ValueError: if the type of the input is not supported
        
        Returns:
            str: the random value as a string
        """
        
        match input.type:
            case constants.Type.INT:
                    return  str(random.randint(constants.INT_MIN, constants.INT_MAX)) if input.len is None else "{" + (str(random.randint(constants.INT_MIN, constants.INT_MAX)) + ", " * input.len) + "}"     
            case constants.Type.SHORT:
                    return  str(random.randint(constants.SHORT_MIN, constants.SHORT_MAX)) if input.len is None else  "{" + (str(random.randint(constants.SHORT_MIN, constants.SHORT_MAX)) + ", " * input.len) + "}" 
            case constants.Type.LONG:
                return str(random.randint(constants.LONG_MIN, constants.LONG_MAX)) if input.len is None else "{" + (str(random.randint(constants.LONG_MIN, constants.LONG_MAX)) + ", " * input.len) + "}"
            case constants.Type.FLOAT:
                return str(random.uniform(constants.FLOAT_MIN, constants.FLOAT_MAX)) if input.len is None else "{" + (str(random.uniform(constants.FLOAT_MIN, constants.FLOAT_MAX)) + ", " * input.len) + "}"
            case constants.Type.DOUBLE:
                return str(random.uniform(constants.DOUBLE_MIN, constants.DOUBLE_MAX)) if input.len is None else "{" + (str(random.uniform(constants.DOUBLE_MIN, constants.DOUBLE_MAX)) + ", " * input.len) + "}"
            case constants.Type.CHAR:
                return "\'" + random.choice(constants.CHARACTERS) + "\'" if input.len is None else "\"" + (random.choice (constants.CHARACTERS) * input.len) + "\""
            case _:
                 raise ValueError(f"Type {input.type} not supported")