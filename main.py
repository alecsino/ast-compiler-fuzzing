import os
import json
from tqdm import tqdm
import multiprocessing as mp
from modules.compiler import Compiler
from modules.importer import Importer
from modules.arg_parser import ArgParser

def main():
    arg_parser = ArgParser()
    args = arg_parser.args 

    compiler = Compiler(args)
    tests = Importer(args)

    #clear data folder
    if os.path.exists('data'):
        for file in os.listdir("data"):
            os.remove(os.path.join("data", file))
    else:
        os.makedirs('data')

    
    #TODO: change this - for now it just takes the c files in the tests directory
    files = []
    for file in os.listdir("tests"):
        if file.endswith(".c"):
            files.append(os.path.join("tests", file))
    
    interesting_tests = []
    # use mp pool to run the tests in parallel
    with mp.Pool(args.num_cores) as pool:
        with tqdm(total=len(files)) as pbar:
            for stats in pool.imap_unordered(compiler.compile_test, files):
                pbar.update()
                if stats is None:
                    continue
                #pop file for the check and then add it back
                file = stats.pop("file")
                if not all(value == stats["last"] for value in stats.values()):
                    stats["file"] = file
                    pbar.set_description_str(str(stats))
                    interesting_tests.append(stats)
            pbar.close()

    for i in interesting_tests:
        min_v = min([value for key, value in i.items() if not key.startswith("file") and not key.startswith("last")])
        i["max_rateo"] = round(i["last"] / min_v, 2)
        if i["max_rateo"] > 1:
            print(i)
            json.dump(i, open(os.path.join("data", i["file"] + ".json"), "w"))

if __name__ == "__main__":
    main()