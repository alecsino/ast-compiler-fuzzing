import os
import json
from tqdm import tqdm
import multiprocessing as mp
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
    
    fuzzer = Fuzzer(tests=tests, compiler=compiler, num_cores=args.num_cores, n_threshold=args.n_threshold)
    fuzzer.fuzz()
    
    
    
if __name__ == "__main__":
    main()