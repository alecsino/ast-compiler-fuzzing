import matplotlib.pyplot as plt
import numpy
import os
from matplotlib import rcParams

def parse_data():
    #read all files in data
    data = {}
    data["compiler_count"] = {}
    data["ticks_count"] = {}
    files_list = os.listdir("./data")
    if files_list == []:
        print("No data found, try running the script from the root directory")
        return
    
    for f in files_list:
        if os.path.isfile(os.path.join("./data", f)):
            with open(os.path.join("./data", f), 'r') as file:
                first_line = file.readline()
                first_line = first_line.split(",")

                if first_line[2] in data["compiler_count"]:
                    data["compiler_count"][first_line[2]] += 1
                else:
                    data["compiler_count"][first_line[2]] = 1

                if float(first_line[5]) > 1.5:
                    first_line[5] = 1.5

                if float(first_line[5]) in data["ticks_count"]:
                    data["ticks_count"][float(first_line[5])] += 1
                else:
                    data["ticks_count"][float(first_line[5])] = 1
    
    return data


data = parse_data()
print(data)

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Tahoma']

fig = plt.figure()
ax = plt.axes()

fig.set_size_inches(5, 3)
fig.subplots_adjust(bottom=0.15)
fig.subplots_adjust(top=0.9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_facecolor("#e3e3e3")

plt.title(f'Frequency', loc="left",  fontsize=9)
COLOR_LIST = ["black", "#850d0f", "#0c4299"]


# plt.ylim(0.25, 25)
plt.xlim(0.90, 1.7)

plt.xlabel('Ratio', fontsize=9)
ticks_data = data['ticks_count']

ticks_values = [ keys for keys, values in ticks_data.items() for i in range(values)] 
ticks_bins = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 8]
ticks_count, _ = numpy.histogram(ticks_values, bins=ticks_bins)

print(ticks_count)
print(ticks_bins)
plt.hist(ticks_values, bins=ticks_bins, color=COLOR_LIST[1],  width=0.09, align="mid")

ticks_pos = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
ticks_bins = [str(i) for i in ticks_bins]
plt.xticks(ticks_pos, ticks_bins)

plt.savefig('./utils/plot.png', dpi=300)
plt.show()

plt.xticks(ticks_bins)


# plt.xlabel('Compiler', fontsize=9)
# compiler_data = data['compiler_count']
# compiler_labels = list(compiler_data.keys())
# compiler_values = list(compiler_data.values())
# plt.bar(compiler_labels, compiler_values, color=COLOR_LIST[1])

# plt.savefig('./utils/plot-compiler.png', dpi=300)
# plt.show()
