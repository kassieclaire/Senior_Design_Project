import os
import sys
# defines
executable = "..\\..\\..\\sim_executable\\cascading_failure_simulator.exe"
# simulations to run and their settings
batch_sizes = [64, 64]
case_names = ["case118", "case118"]
iterations_list = [10000, 10000]
f_list = [2, 2]
r_list = [.7, .8]
e_list = [.1, .2]
theta_list = [.1, .2]
for i in range(len(batch_sizes)):
    output_name = case_names[i] + "_" + str(f_list[i]) + "_" + str(r_list[i]).split(
        '.')[1] + "_" + str(theta_list[i]).split('.')[1] + "_" + str(e_list[i]).split('.')[1]
    arguments = case_names[i] + " " + str(iterations_list[i]) + " " + str(f_list[i]) + " " + str(
        r_list[i]) + " " + str(theta_list[i]) + " " + str(e_list[i]) + " " + output_name + " " + str(batch_sizes[i])
    print(arguments)
    os.system(executable + " " + arguments)

print(executable)
