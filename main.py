import os
from modules.compiler import Compiler
from modules.data_loader import DataLoader
from modules.arg_parser import ArgParser
from modules.fuzzer import Fuzzer

def main():
    arg_parser = ArgParser()
    args = arg_parser.args 

    compiler = Compiler(args)
    data_loader = DataLoader()
    
    tests = data_loader.tests()
    
    if not os.path.exists('data'):
        os.makedirs('data')

    for file in os.listdir("data"):
        os.remove(os.path.join("data", file))
    
    fuzzer = Fuzzer(tests=tests, compiler=compiler, num_cores=args.num_cores, n_threshold=args.threshold)
    interesting_tests = fuzzer.fuzz()

    data_loader.save_results(interesting_tests, args)
        
    
    
    
if __name__ == "__main__":
    main()