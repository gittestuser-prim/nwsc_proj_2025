import subprocess
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: wrapper.py filename.conf")
        print("Please see example config File")
    config = []
    with open(sys.argv[1], 'r') as file:
        config.append([line.rstrip() for line in file])

    for idx, entry in config:
        subprocess.run(['python', 'proj.py', int(config[idx][0]), float(config[idx][1]),
                    float(config[idx][2]), int(config[idx][3]), int(config[idx][4]),
                        float(config[idx][5]), str(config[idx][6]), str(config[idx][7])])

if __name__ == '__main__':
    main()

    print("Usage: python3 proj.py patients(int) infection rate(float 0-1) incubating infection rate(float 0-1)"
          + " timesteps from incubating to infected(int) recovery time(int) recovery chance(float 0-1)"
          + "incubating active (True or False)+ mode(max, rnd, first, last)")