import subprocess
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: wrapper.py filename.conf")
        print("Please see example config File")
    config = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            line = line.strip()
            config.append(line.split(' '))

    print("Config is: ")
    print(config)

    # need to cast all as str for kwargs to work properly, original types are restored in main file
    for idx, entry in enumerate(config):
        print("Current run: " + str(idx+1))
        subprocess.run(['python3', 'proj.py', str(config[idx][0]), str(config[idx][1]),
                    str(config[idx][2]), str(config[idx][3]), str(config[idx][4]),
                        str(config[idx][5]), str(config[idx][6]), str(config[idx][7])])

if __name__ == '__main__':
    main()

    print("Usage: python3 proj.py patients(int) infection rate(float 0-1) incubating infection rate(float 0-1)"
          + " timesteps from incubating to infected(int) recovery time(int) recovery chance(float 0-1)"
          + "incubating active (True or False)+ mode(max, rnd, first, last)")