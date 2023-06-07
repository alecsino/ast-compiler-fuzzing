import os
import subprocess
input_dir = "./output/"
test_folder = "./input"

FLAGS = ["-O", "-fno-unroll-loops", "-w"]

def main():
    #for each file in input_dir
    for file in os.listdir(input_dir):
        print("Checking file: " + file)
        #read the first line
        line = ""
        with open(os.path.join(input_dir, file), "r") as f:
            file_content = f.read()
            line = file_content.split("\n")[0].strip().split(",")
        
        #remove name from file path
        file_path = os.path.dirname(line[0])
        compiler = [line[1], line[2]]

        #remove from first line to "Flags:", so we just have the c file
        for i in range(len(file_content.split("\n"))):
            if file_content.split("\n")[i].strip().startswith("Flags:"):
                #get the opt level from the string Flags: ON
                opt_level = file_content.split("\n")[i].strip().split(" ")[1]
                FLAGS[0] = opt_level
                file_content = "\n".join(file_content.split("\n")[i+1:])
                break

        #save this file in file_path
        file_name = os.path.basename(line[0])
        c_path = os.path.join(file_path, "tmp_" + file_name)

        with open(c_path, "w") as f:
            f.write(file_content)
        # print("File saved in: " + c_path)
        
        not_compiled = False
        for i in compiler:
            result = subprocess.run([i, c_path, "-o", "tmp-"+i, "-fsanitize=address,undefined"] + FLAGS, stderr=subprocess.PIPE)
            if result.stderr:
                print("Error compiling file: " + c_path)
                print(result.stderr.decode("utf-8"))
                not_compiled = True
                break
            #run it
            try:
                result = subprocess.run(["./tmp-"+i], stderr=subprocess.PIPE, timeout=5)
            except subprocess.TimeoutExpired:
                print("Timeout, but still safe")
            if result.stderr:
                print("Error running file: " + c_path)
                print(result.stderr.decode("utf-8"))
            os.remove("tmp-"+i)

        if not_compiled:
            os.remove(c_path)
            continue

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

        #if expected != got, print error
        if int(s_lines[0]) != int(s_got[0]) or int(s_lines[1]) != int(s_got[1]):
            print("Lines not matched for file: " + file)
            print("Expected: " + str(s_lines))
            print("Got: " + str(s_got))


        os.remove(c_path)
        # exit(1)
        
main()