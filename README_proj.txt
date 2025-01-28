Simple simulator for disease spread on an open dataset (see dataset readme)

Currently two parameters still fixed and needed to be changed in code if you want to another dataset: (numpy dimension is the number of nodes, timestamp is the beginning of the simulation in linux time)

Program has 2 modes:
Primary mode with changes of hyper parameters in code will print out every 1000 steps with a graph layout and a plot at the end.
CLI mode can be used with batchscripts. writes plot into file, as well as appends data in csv to an output file.

Usage: 
   python3 proj.py patients(int) infection rate(float 0-1) incubating infection rate(float 0-1)
   timesteps from incubating to infected(int) recovery time(int) recovery chance(float 0-1)
   incubating active (True or False)+ mode(max, rnd, first, last)
Example:
python3 proj.py 3 1 0.2 10 500 0.1 False rnd

plot name:
        plt.savefig("plot" + str(num_pat) + str(mode) + ".png")
        Fileoutput into: infectious_output.txt
