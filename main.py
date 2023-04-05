import os
from modules.compiler import Compiler
from modules.importer import Importer
from modules.arg_parser import ArgParser

arg_parser = ArgParser()
args = arg_parser.args

compiler = Compiler(args)
tests = Importer(args)

if not os.path.exists('data'):
    os.makedirs('data')