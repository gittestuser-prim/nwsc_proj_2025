import math
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import sys

# formats our timetable, who is meeting whom at what time
# return list in format: [time, [a,b],[b,c]...]
def time(e, start):
    e_final = []
    for t in e:
        t[0] = t[0] - start
    e_new = sorted(e, key=lambda x: x[0])

    t_run = -1
    for t in e_new:
        if t_run != t[0]:
            t_run = t[0]
            e_final.append([t[0], t[1]])
        else:
            e_final[-1].append(t[1])

    return e_final


#returns the list of actors that were meeting at the specified timestamp:
def get_actors(list, time):
    for actor in list:
        if actor[0] == time:
            return actor[1:]
        elif actor[0] > time:
            return []


# load the file and converts it into a 2d extended adjacency matrix where its either 0 if
# no connection or the timestamps if there was contact (number of timestamps also indicate how often)
# data diminesions are currently hardcoded, need to be parsed from file afterwards

def load_data(path):
    f = open(path, "r")
    data = np.zeros((410, 410), dtype=object)

    # random timestamp
    time_stamp = 1247658199
    time_table = []
    for line in f:

        da = line.split(" ")
        da = [int(x) for x in da]

        if da[3] < time_stamp:
            time_stamp = da[3]

        if data[(da[0]-1)][(da[1]-1)] == 0:
            data[(da[0]-1)][(da[1]-1)] = [da[3]]
        else:
            temp = data[(da[0]-1)][(da[1]-1)]
            temp.append(da[3])
            data[(da[0]-1)][(da[1]-1)] = temp
        time_table.append([da[3], [da[0], da[1]]])

    return data, time(time_table, time_stamp)


def gen_Aij(d):
    # converts the time matrix into a pure adjacency matrix
    aij = np.zeros(d.shape, dtype=int)
    for idx, x in  enumerate(d):
        for idy, y in  enumerate(x):
            if y != 0:
                aij[idx][idy] = 1
    return aij


def setup(G, time_table, pat, mode, n_nodes, ino):
    patients = []
    idx = 0
    if mode == 'max':
        degree_sequence = sorted(G.degree, key=lambda x: x[1], reverse=True)
        #print(degree_sequence)
    while len(patients) < pat:
        if mode == 'rnd':
            new = random.randint(1,n_nodes)
            if not new in patients and not new in ino:
                patients.append(new)
        elif mode == 'max':
            patients.append(degree_sequence[idx][0])
            idx += 1
        elif mode == 'first':
            if time_table[idx][1][0] in patients:
                idx += 1
            else:
                patients.append(time_table[idx][1][0])
                idx += 1
        elif mode == 'last':
            if time_table[-idx][1][0] in patients:
                idx += 1
            else:
                patients.append(time_table[-idx][1][0])
                idx += 1
        else:
            print("invalid mode")
            return None
    #print(patients)
    return patients

def compute_SI(inf, sus, time, la, s0):
    N = inf + sus
    # I(t)=1/(1+(1/(N- S0)-1)*exp(-λt))
    return 1/(1+(1/(N-s0)-1) * math.exp(-la*time))

def find_maxdeg(g):
    deglist = dict(g.degree())
    v = sum(deglist.values())/float(len(deglist))
    print(v)
    return v

def main():

    # load data:
    data, time_table = load_data("out.sociopatterns-infectious")
    Aij = gen_Aij(data)
    G = nx.from_numpy_array(Aij)
    num_nodes = G.number_of_nodes()

    if len(sys.argv) < 2:
        print("Network Science Project Infectious - Spreading Sickness")
        print("If you want to run the program with args on commandline, please follow the following instructions:")
        print("Usage: python3 proj.py patients(int) infection rate(float 0-1) incubating infection rate(float 0-1) "
              + "timesteps from incubating to infected(int) recovery time(int) recovery chance(float 0-1) "
              + "incubating active (True or False) mode(max, rnd, first, last) "
              + "inoculation(list with node numbers or 0 if random node(s))")
        print("Example: python3 proj.py 3 1 0.2 10 500 0.1 False rnd [0,0]")
        # Parameters:
        # num_pat: Number of initial Patients
        # i_rate: infection rate per social interaction
        # i_rate_small: chance of incubating persons to infect someone
        # inc_time: How many timesteps(20s) until infected
        # rec_time: timesteps it takes for recovery to begin - set this larger than 25000 to disable recovery
        # rec_chance: chance to recover (increases with time after rec_time)
        # incubating: enable incubate phase or directly infect
        num_pat = 30
        i_rate = 1
        i_rate_small = 0.2
        inc_time = 10
        rec_time = 25000
        rec_chance = 0.1
        incubating = False
        inoculation = []
        # Modes are: rnd, max, first, last
        mode = 'first'
    else:
        if len(sys.argv) != 11:
            print("Error, wrong number of parameters")
        num_pat = int(sys.argv[1])
        i_rate = float(sys.argv[2])
        i_rate_small = float(sys.argv[3])
        inc_time = float(sys.argv[4])
        rec_time = float(sys.argv[5])
        rec_chance = float(sys.argv[6])
        if sys.argv[7] == 'True':
            incubating = True
        else:
            incubating = False
        mode = str(sys.argv[8])

        # Inoculation setup
        tmp = str(sys.argv[9])
        inoculation = []
        if tmp.isdigit():
            while len(inoculation) < int(tmp):
                new = random.randint(1, num_nodes)
                if not new in inoculation:
                    inoculation.append(new)

        if tmp != []:
            tmp_list = tmp.strip("'[]'").split(',')
            for i in tmp_list:
                if i.isdigit():
                    inoculation.append(int(i))
        for i in inoculation:
            if i == 0:
                i = random.randint(1, num_nodes)
                while i in inoculation:
                    i = random.randint(1, num_nodes)
        runner = int(sys.argv[10])

    # ---------------------------------------
    # Setup start:
    infected_stats = []
    susceptible_stats = []
    incubating_stats = []
    recovered_stats = []
    inoculated_stats = []

    time_stats = []
    color_map = []
    attr = []
    time_in_state_logic = []
    # avg_degree = find_maxdeg(G)
    patient_zero = setup(G, time_table, num_pat, mode, num_nodes, inoculation)
    if patient_zero is None:
        print("Something went wrong, terminating program")
        return
    pos = nx.spring_layout(G, k=0.35, iterations=20)

    # Set up our infection schema and inoculate people:

    for node in G:
        time_in_state_logic.append(0)
        if node in patient_zero:
            attr.append('Infected')
            color_map.append('red')
        elif node in inoculation:
            attr.append('Inoculated')
            color_map.append('violet')
        else:
            attr.append('Susceptible')
            color_map.append('green')
    time_current = 0


    # -----------------------------------------------
    # Game Start:
    while time_current <= time_table[-1][0]:
        happening = get_actors(time_table, time_current)
        # this is only meetings (only infection spread when meeting)
        if happening:
            for encounter in happening:
                if attr[encounter[1] - 1] == 'Recovered' or attr[encounter[1] - 1] == 'Inoculated':
                    continue
                if attr[encounter[0]-1] == 'Infected':
                    if random.random() < i_rate and incubating:
                        attr[encounter[1]-1] = 'Incubating'
                        color_map[encounter[1]-1] = 'orange'
                        time_in_state_logic[encounter[1]-1] = time_current
                    elif random.random() < i_rate and not incubating:
                        attr[encounter[1]-1] = 'Infected'
                        color_map[encounter[1]-1] = 'red'
                        time_in_state_logic[encounter[1]-1] = time_current

                if attr[encounter[0]-1] == 'Incubating':
                    if random.random() < i_rate_small:
                        attr[encounter[1]-1] = 'Incubating'
                        color_map[encounter[1]-1] = 'orange'
                        time_in_state_logic[encounter[1]-1] = time_current

        # time - State transition logic - this is outside of meetings
        for idx, x in enumerate(time_in_state_logic):
            if x != 0:
                if attr[idx] == 'Infected':
                    rec_t_cur =  x + rec_time*20
                    if rec_t_cur <= time_current:
                        if random.random() < (time_current - rec_t_cur) * rec_chance:
                            attr[idx] = 'Recovered'
                            color_map[idx] = 'blue'
                            time_in_state_logic[idx] = time_current

                elif attr[idx] == 'Incubating':
                    if (x + inc_time*20) == time_current:
                        attr[idx] = 'Infected'
                        color_map[idx] = 'red'
                        time_in_state_logic[idx] = time_current
                else:
                    continue

        # These are for statistics only
        infected_stats.append(attr.count('Infected'))
        susceptible_stats.append(attr.count('Susceptible'))
        incubating_stats.append(attr.count('Incubating'))
        recovered_stats.append(attr.count('Recovered'))
        inoculated_stats.append(attr.count('Inoculated'))

        time_stats.append(time_current)
        # if incubators are ready to be infected

        #draw the graph every 100 episodes:

        if time_current%1000 == 0:
            if len(sys.argv) < 2:
                print("Current time: " + str(time_current) + " | Healthy: " + str(susceptible_stats[-1]) +
                      " | Incubating: " + str(incubating_stats[-1]) +
                      " | Infected: " + str(infected_stats[-1])  +
                      " | Recovered: " + str(recovered_stats[-1]))
            nx.draw(G, node_color=color_map, pos=pos)
            filename = "graph" + str(time_current) + ".png"
            plt.savefig(filename)
            plt.close()

        time_current = time_current + 20



    # ------------------------------------------------
    # Report and Drawings

    plt.title("Overview Infections")
    plt.plot(time_stats, infected_stats, lw=1.4, color='red', label='Infected')
    plt.plot(time_stats, susceptible_stats, lw=1.4, color='green', label='Susceptible')
    plt.plot(time_stats, incubating_stats, lw=1.4, color='orange', label='Incubating')
    plt.plot(time_stats, recovered_stats, lw=1.4, color='blue', label='Recovered')
    plt.plot(time_stats, inoculated_stats, lw=1.4, color='violet', label='Inoculated')
    plt.ylabel('Infections')
    plt.legend()
    plt.xlabel('Time in 20s')
    if len(sys.argv) > 1:
        plt.savefig("plot" + str(num_pat) + str(mode) + "_" + str(runner) +".png")
        with open("infectious_output.txt", "a") as f:
            f.write(str(infected_stats[-1]) + ";" + str(susceptible_stats[-1])
                    + ";" + str(incubating_stats[-1]) + ";" + str(recovered_stats[-1]) + "\n")
    else:
        plt.show()

if __name__ == '__main__':
    main()
