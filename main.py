import os
from modules.compiler import Compiler
from modules.importer import DataLoader
from modules.arg_parser import ArgParser

def main():
    arg_parser = ArgParser()
    args = arg_parser.args 

    compiler = Compiler(args)
    data_loader = DataLoader()
    
    if not os.path.exists('data'):
        os.makedirs('data')
    


if __name__ == "__main__":
    main()