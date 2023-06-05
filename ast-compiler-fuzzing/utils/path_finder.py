import os

input_dir = "./output/O2"
test_folder = "./input"

def main():
    #for each file in input
    for file in os.listdir(input_dir):
        #read the first line of the file
        line = ""
        with open(os.path.join(input_dir, file), "r") as f:
            file_content = f.read()
            line = file_content.split("\n")[0].strip().split(",")
        
        file_name = line[0]
        #extract the file name
        file_name = file_name.split("/")[-1]
        #find this file name in test_folder, there can be multiple
        #the folder has also subfolders that we need to check
        file_paths = []
        file_path = ""
        for root, dirs, files in os.walk(test_folder):
            for name in files:
                if name == file_name:
                    file_paths.append(os.path.join(root, name))
        
        if len(file_paths) == 0:
            print(f"File {file_name} not found")
            return
        
        if len(file_paths) > 1:
            print(f"File {file_name} found multiple times")
            print("Which is the correct one?")
            # request input asking for 1, ..., len(file_paths)
            # and then use that index to get the correct file_path
            for i, file_path in enumerate(file_paths):
                print(f"{i+1}: {file_path}")
            index = int(input("Which one?"))
            if index < 1 or index > len(file_paths):
                print("Invalid input")
                return
            
            file_path = file_paths[index-1]
        
        if len(file_paths) == 1:
            file_path = file_paths[0]
        
        #set this path in the file instad of the file name
        line[0] = file_path
        #write the file back
        with open(os.path.join(input_dir, file), "w") as f:
            f.write(",".join(line))
            f.write("\n")
            #write the rest of the file without the first line
            f.write("\n".join(file_content.split("\n")[1:]))


main()


