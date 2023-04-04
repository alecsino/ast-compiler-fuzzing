import os
from modules.compiler import Compiler
from modules.importer import Tests

compiler = Compiler()
tests = Tests()

if not os.path.exists('data'):
    os.makedirs('data')