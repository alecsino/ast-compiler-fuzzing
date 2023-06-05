import os
import subprocess
input_dir = "./output/O2"
test_folder = "./input"

FLAGS = ["-O2", "-fno-unroll-loops", "-w"]

def main():
    #for each file in input_dir
    for file in os.listdir(input_dir):
        #read the first line
        line = ""
        with open(os.path.join(input_dir, file), "r") as f:
            file_content = f.read()
            line = file_content.split("\n")[0].strip().split(",")
        
        #remove name from file path
        file_path = os.path.dirname(line[0])
        compiler = [line[1], line[2]]

        #remove first line from file_content
        file_content = "\n".join(file_content.split("\n")[1:])

        #if first line starts with "Flags:" also remove it
        if file_content.startswith("Flags:"):
            file_content = "\n".join(file_content.split("\n")[1:])

        #remove lines containing '+' as first char
        file_content = "\n".join([line for line in file_content.split("\n") if not line.strip().startswith("+")])

        #remove char '-' if first char in line
        file_content = "\n".join([line[1:] if line.strip().startswith("-") else line for line in file_content.split("\n")])

        #remove lines with '?' as first char
        file_content = "\n".join([line for line in file_content.split("\n") if not line.strip().startswith("?")])

        #save this file in file_path
        file_name = os.path.basename(line[0])
        c_path = os.path.join(file_path, "tmp_" + file_name)

        with open(c_path, "w") as f:
            f.write(file_content)
        print("File saved in: " + c_path)
        
        #compile this file with FLAGS

        # for i in compiler:
        #     result = subprocess.run([i, c_path, "-o", "-fsanitize=address,undefined", "tmp-"+i] + FLAGS, stderr=subprocess.PIPE)
        #     if result.stderr:
        #         print("Error compiling file: " + c_path)
        #         print(result.stderr.decode("utf-8"))
        #         exit(1)

        s_lines = [line[3], line[4]]
        s_got = []
        for i in compiler:
            result = subprocess.run([i, c_path] + FLAGS + ["-S", "-o", "tmp-"+i+".s"], stderr=subprocess.PIPE)
            if result.stderr:
                print("Error compiling file: " + c_path)
                print(result.stderr.decode("utf-8"))
                exit(1)
            with open("tmp-"+i+".s", "r") as f:
                #n lines without comments or directives
                n = 0
                for line in f.readlines():
                    line = line.strip()
                    if line.startswith('#') or line.startswith('.'):
                        continue  
                    n += 1
                s_got.append(n)
            os.remove("tmp-"+i+".s")
        
        print("Expected: " + str(s_lines))
        print("Got: " + str(s_got))

        os.remove(c_path)
        # exit(1)
        
main()