import os
from modules.compiler import Compiler
from modules.data_loader import DataLoader
from modules.arg_parser import ArgParser
from modules.fuzzer import Fuzzer
from modules.strategies.mutator import Mutator

def main():
    arg_parser = ArgParser()
    args = arg_parser.args 

    compiler = Compiler(args)
    data_loader = DataLoader(args)
    mutator = Mutator()
    tests = data_loader.tests()
    
    folders_used = ["data", "err", ".tmp"]
    for folder in folders_used:
        if not os.path.exists(folder):
            os.makedirs(folder)

        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))

    fuzzer = Fuzzer(tests=tests, compiler=compiler, num_cores=args.num_cores, n_threshold=args.threshold, mutator=mutator)

    interesting_tests = fuzzer.fuzz()
    print(f"Found {len(interesting_tests)} interesting tests")
    data_loader.save_results(interesting_tests, args)

    # Clean up - removes all the files created by the fuzzer in the tests folder
    # remove all files that begins with "tmp_"
    print("Clean up in progress")
    for root, dirs, files in os.walk(args.data):
        for file in files:
            if file.startswith("tmp_"):
                os.remove(os.path.join(root, file))

        
    
    
    
if __name__ == "__main__":
    main()