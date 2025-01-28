import subprocess
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: wrapper.py filename.cfg")
        print("Please see example config File")
    config = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            line = line.strip()
            config.append(line.split(' '))

    # need to cast all as str for kwargs to work properly, original types are restored in main file
    for idx, entry in enumerate(config):
        print("Current run: " + str(idx+1))
        print("Config: " + str(entry))
        subprocess.run(['python3', 'proj.py', str(config[idx][0]), str(config[idx][1]),
                    str(config[idx][2]), str(config[idx][3]), str(config[idx][4]),
                        str(config[idx][5]), str(config[idx][6]), str(config[idx][7])])

if __name__ == '__main__':
    main()